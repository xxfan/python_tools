#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import json

MODEL_CONTENT_HEAD = """

#sys
import datetime
#sqlalchemy
from sqlalchemy.sql import func
import sqlalchemy
from sqlalchemy import create_engine, text, Column, ForeignKey, and_, or_, func, Index, Boolean, Integer, Text, String, DateTime, Float, UniqueConstraint, primary keyConstraint
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.dialects.mysql import VARCHAR, BIGINT, TINYINT, DATETIME, TIMESTAMP, TEXT, ENUM, FLOAT, INTEGER, BLOB,BOOLEAN,JSON
from sqlalchemy.sql.expression import desc
from sqlalchemy.inspection import inspect
from sqlalchemy import distinct

from db.models.base_model import BaseModel

"""


#驼峰命名格式转下划线命名格式
def camel_to_underline(camel_format):
    underline_format = ''
    if isinstance(camel_format, str):
        for _s_ in camel_format:
            underline_format += _s_ if _s_.islower() else '_' + _s_.lower()
    return underline_format


#下划线命名格式驼峰命名格式
def underline_to_camel(underline_format):
    camel_format = ''
    if isinstance(underline_format, str):
        for _s_ in underline_format.split('_'):
            camel_format += _s_.capitalize()
    return camel_format


def create_sql(table):
    title = table[0]
    table = table[1:]
    table_name = title[0]

    line = "CREATE TABLE  IF NOT EXISTS `%s`(\n" % table_name
    for cells in table:
        nullable = bool(int(cells[title.index('nullable')]))
        default = cells[title.index('default')]
        is_pkey = int(cells[title.index('primary key')])
        _type = cells[title.index('type')].upper()

        column_name = cells[0]
        
        null_str = ""
        df_str = ""
        ai_str = ""

        if ('AUTO_INCREMENT' in title and cells[title.index('AUTO_INCREMENT')] != ''
                and int(cells[title.index('AUTO_INCREMENT')])):
            ai_str = "AUTO_INCREMENT"

        if not nullable:
            null_str = "NOT NULL"

        if (default.upper() not in ["NULL","NONE"] 
                and _type.upper() not in ['JSON', "TEXT"]):
            df_str = " DEFAULT %s" % (default)

        line += "   `%s` %s %s %s %s,\n" % (column_name, _type, null_str, df_str, ai_str)

    pkeys = []
    for cells in table:
        column_name = cells[0]
        is_pkey = cells[title.index('primary key')]
        if int(is_pkey) > 0:
            pkeys.append(column_name)

    line += "   `is_deleted` BOOLEAN DEFAULT 0,\n"
    line += "   `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 默认属性\n"
    line += "   `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 默认属性\n"
    line += "   PRIMARY KEY (%s),\n" % (str(pkeys).replace('\'','`').replace('[','').replace(']',''))

    for cells in table:
        column_name = cells[0]
        need_index = cells[title.index('index')]
        if need_index == '1':
            line += "   KEY `idx_%s` (`%s`) ,\n" % (column_name, column_name)

    line = line[0:-2]
    line += "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='%s';\n\n" % table_name
    return line


def create_model(table):
    title = table[0]
    table = table[1:]
    table_name = title[0]

    line = "class %s(BaseModel):\n" % (underline_to_camel(table_name))
    line += "   __tablename__ = '%s'\n" % table_name
    line += "   __table_args__ = (\n"

    pkeys = []
    for cells in table:
        column_name = cells[0]
        is_pkey = cells[title.index('primary key')]
        if int(is_pkey) > 0:
            pkeys.append(column_name)

    line += "       PrimaryKeyConstraint(%s),\n" % (str(pkeys).replace('[','').replace(']',''))

    for cells in table:
        need_index = cells[title.index('index')]
        column_name = cells[0]
        if need_index == '1':
            line += "       Index('idx_%s', '%s'),\n" % (column_name, column_name)

    line += "       {\n"
    line += "           'mysql_engine': 'InnoDB',\n"
    line += "           'mysql_charset': 'utf8'\n"
    line += "       }\n"
    line += "   )\n"
    line += "\n"

    for cells in table:
        nullable = bool(int(cells[title.index('nullable')]))
        is_pkey = cells[title.index('primary key')]
        column_name = cells[0]
        default = cells[title.index('default')]
        _type = cells[title.index('type')].upper()

        if 'UNSIGNED' in _type:
            _type = _type.replace(' UNSIGNED', '')
            if ')' in _type:
                _type = _type.replace(')', ',unsigned=True)')
            else:
                _type = _type + '(unsigned=True)'


        null_str = ""
        df_str = ""
        ai_str = ""

        if 'AUTO_INCREMENT' in title and cells[title.index('AUTO_INCREMENT')] and int(cells[title.index('AUTO_INCREMENT')]):
            ai_str = ",autoincrement=True"

        if not nullable:
            null_str = ",nullable=False"

        if default.upper() not in ['NULL',"NONE"] and _type.upper() not in ['JSON', "TEXT"]:
                df_str = ",default=%s" % (default)

        line += "   {name} = Column({_type}{default}{nullable}{autoincrement})\n".format(
            name=column_name, _type=_type, default=df_str, nullable=null_str, autoincrement=ai_str)

    line += "   is_deleted = Column(Boolean, nullable=False, default = False)\n"
    line += "   updated_time = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now, onupdate=datetime.datetime.now)\n"
    line += "   created_time = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now)\n\n\n"

    return line


def split_tables(lines):
    def _split_one_table(start_line_id, lines):
        none_null_line_id = None        
        for _i_ in range(start_line_id, len(lines)):
            if lines[_i_] and lines[_i_][0]:
                none_null_line_id = _i_
                break

        if none_null_line_id is None:
            return None, len(lines)

        rows = []
        for _i_ in range(none_null_line_id, len(lines)):
            if lines[_i_] and lines[_i_][0]:
                rows.append(lines[_i_])
                print(lines[_i_])
            else:
                return rows, _i_ + 1

        return None,len(lines)

    #start
    tables = []
    line_id = 0
    while line_id < len(lines):
        table, line_id = _split_one_table(line_id, lines)
        print(line_id)
        if table:
            tables.append(table)

    return tables


def analysis_csv(csv_path):
    def _remove_annotation(tmp):
        end = tmp.find('#')
        if end != -1:
            tmp = tmp[0:end]
        return tmp

    lines = []
    with open(csv_path, 'r') as f:
        while True:
            line = f.readline().strip()
            if not line:
                break

            cells = []
            for c in line.split(','):
                cells.append(_remove_annotation(c).strip())

            lines.append(cells)
    return lines


def export_file(csv_path):
    lines = analysis_csv(csv_path)

    tables = split_tables(lines)

    file_name = csv_path.split('/')[-1].split('.')[0]
    model_f = open('./%s_model.py' % file_name, 'w')
    sql_f = open('./%s_tables.sql' % file_name, 'w')

    model_f.write(MODEL_CONTENT_HEAD)

    for table in tables:
        line_m = create_model(table)
        model_f.write(line_m)
        line_s = create_sql(table)
        sql_f.write(line_s)

    model_f.close()
    sql_f.close()


if __name__ == "__main__":
    csv_path = sys.argv[1]
    print("csv_path:", csv_path)
    print("start exporting.")
    export_file(csv_path)
    print("it's over.")
