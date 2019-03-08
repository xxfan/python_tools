
## 简介
`csv2sql.py` 用于帮助你快速从csv文件同时生成`mysql建表语句`和`SQLachemy model`.


## 表格填写要求:
- 每个表的第一行必须是固定格式的title
- title的第一列为自定义的表名, 其他列内容固定
- 表名要求用下划线命名格式, 如: matrix_sevenfit_training_record
- 单元格内运行用#号作为注释
- 单元格内的所有空格会被自动删除
- 不需要填写`created_time`, `updated_time`, `is_deleted`这三个字段, 脚本会给每个表都加上这些字段.

## 目前支持的title:
- type : 字段类型
- nullable : 是否允许为空, 可选值 0,1
- default : 默认值(说明, 如果default值为NULL会被忽略, type为JSON或TEXT时default的值也会被忽略)
- primary key : 是否为主键, 可选值 0,1
- index : 是否为索引, 可选值 0,1
- AUTO_INCREMENT : 是否自增, 可选值 0,1(说明: 如果为自增字段, 参数名必须为id)


## 导出规则:
- 运行脚本 `python csv2sql.py xxx.csv`, 其中xxx需要替换为你的实际文件名称, 运行后,会在当前目录导出为xxx_model.py和xxx_tables.sql
- model的class name为表名转换为驼峰格式, 如: MatrixSevenfitTrainingRecord
- 生成的model 继承父类BaseModel, 需要自己实现BaseModel
- 如果default值为NULL会被忽略, 字段type为JSON或TEXT时default的值也会被忽略

## 补充:
如果导出内容不符合您的要求, 你可以自己修改脚本

