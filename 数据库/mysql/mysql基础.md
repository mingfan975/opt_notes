<!-- TOC -->

- [mysql基础](#mysql基础)
  - [配置文件](#配置文件)
  - [常见引擎](#常见引擎)
  - [基础命令](#基础命令)
  - [常用关键字](#常用关键字)
    - [where](#where)
    - [group by(分组)](#group-by分组)
    - [having(分组筛选)](#having分组筛选)
    - [distinct(去重)](#distinct去重)
    - [order by(排序)](#order-by排序)
    - [limit(限制展示条数)](#limit限制展示条数)
    - [正则表达式](#正则表达式)
    - [联表查询](#联表查询)
    - [子查询](#子查询)
  - [数据类型](#数据类型)
  - [约束条件](#约束条件)
  - [视图](#视图)
  - [触发器](#触发器)
  - [事务](#事务)
    - [事务隔离级别](#事务隔离级别)
  - [存储过程](#存储过程)
  - [函数](#函数)
  - [流程控制](#流程控制)
  - [常见故障处理方式](#常见故障处理方式)

<!-- /TOC -->

# mysql基础

[MySQL 和 InnoDB](https://draveness.me/mysql-innodb/)

## 配置文件

## 常见引擎

1. Innodb： 5.5 版本之后的默认引擎， 支持事务、行锁、外键 相比其他引擎数据更加安全；创建表会生成两个文件： 
    表结构文件
    表数据文件

2. MyIsam： 5.5版本之前默认的引擎，虽然在数据安全上没有Innodb可靠， 但是查询速度更快；创建表会生成三个文件： 
     表结构文件
   ​ 表数据文件
   ​ 表索引文件

3. memory： 内存引擎，存储临时数据；创建表的时候会生成一个文件
   ​ 表结构文件

4. blackhole:  黑洞；创建表的时候会生成一个文件
    表结构文件


## 基础命令

 * 创建表模版

   ```sql
   create table 库名.表名(
       字段名1 类型[(宽度) 约束条件],
       字段名2 类型[(宽度) 约束条件],
       字段名3 类型[(宽度) 约束条件]
   );
   ```

* 修改密码

  ```bash
  # 1. 直接登陆设置
  mysql> set password for root@localhost = password("password");
  
  # 2. 使用mysqladmin
  mysqladmin -u username -p old_pwd password "new_password"
  mysqladmin -uroot -p 123456 password "password"
  
  # 3. 使用update
  mysql> update user set password=password(‘123’) where user=’root’ and host=’localhost’; 
  
  
  ## 忘记密码 
  # 1) 关闭当前mysql服务器
  # 2) 跳过用户名和密码验证
  mysqld --skip-grant-tables
  # 3) 无密码连接
  mysql -u root -p 
  # 4) 修改密码
  update mysql.user set password=password("password") where user="root";
  # mysql 5.7 设置密码 
  update mysql.user set authentication_string=password('12345678') where user='root';
  # 5) 刷新权限 
flush privileges;
  # 6) 退出重新登录
  ```
  
  



* 库的增删改查

  ```sql
  -- 创建数据库
  create database db_name charset="utf-8";
  
  -- 查询数据库
  show databases; | show dbs; -- 查询所有
  show create database db_name; -- 查询单个
  show engines; -- 查看数据库引擎
  
  -- 修改数据库
  alter database db_name charset="utf-8";
  
  -- 删除数据库
  drop database db_name;
  ```

* 表的增删改查

  ```sql
  -- 查看当前数据库
  select database();
  
  -- 切换数据库
  use db_name;
  
  -- 创建表
  create table t1(id int, name char(4), age int, des varchar(1000))
  
  -- 查询表
  show tables;  -- 查看当前数据库下的所有表名
  show create table t1;  -- 查看某表的字段
  describe t1;  -- desc t1; 查看某表的字段
  
  -- 修改表
  alter table t1 modify name char(16);
  alter table name remane new_name
  
  -- 添加字段
  alter table table_name add 字段名 字段类型(宽度) 约束条件;
  alter table table_name add 字段名 字段类型(宽度) 约束条件 first;
  alter table table_name add 字段名 字段类型(宽度) 约束条件 after 字段名
  
  --删除表
  drop table t1;
  ```

  



* 数据的增删改查

  ```sql
  -- 添加数据
  insert into  t1 values(1,"zhangsan", 18, "asdererwe")
  
  -- 查询数据
  select * from t1;
  select id, name from t1;
  select * from t1 where name="zhangsan";
  -- char_length统计字段长度
  select char_length(name) from t1;
  
  -- 修改数据
  update t1 set name="lisi" where id = 1;
  
  -- 删除数据
  delete from t1; -- 清空表
  delete from t1 where id = 1;
  
  ```

  

* 模糊查询

  ```sql
  -- 查看严格模式
  show variables like "%mode";
  -- 模糊查询：
  	 -- %: 匹配任意多个字符
  	 -- _: 匹配任意单个字符
  
  -- 修改严格模式
  set session -- 当前窗口有效 
  set global -- 全局有效
  set global sql_mode="STRICT_TRANS_TABLES,PAD_CHAR_TO_FULL_LENGTH"; -- 开启严格模式, 取消mysql自动剔除空格的操作
  ```

  

## 常用关键字

```sql
create table emp(
	id int not null unique quto_increment,
  name varchar(20)  not null,
  sex enum('male','female') not hull default 'male',
  age int unsigned not null, 
  hire_date date not null, 
  post varchar(50), -- 部门名称
  post_comment varchar(120),-- 部门描述
  salary double(15,2),
  office int,
  depart_id int
);

```

### where

```sql
-- 查询连续范围内的数据
select id, name, age from emp where id >=4 and id <=6;
select id, name, age from emp where id between 4 and 6;

-- 查询指定数据， 非连续
select * from emp where salary= 2000 or salary=1800;
select * from emp where salary in (2000, 1800)
select * from emp where salary not in (2000, 1800)

-- 模糊查询
select name, salary from emp where name like '%L%';

-- 查询员工姓名由4个字符组成的姓名和薪资
select name,salary from emp where name like '____';
select name,salary from emp where char_length(name)=4;

-- 包含空/非空
select name, post from emp where post_comment is NULL;
select name, post from emp where post_comment is not NULL;
```



### group by(分组)

分组之后， 最小可操作单位应该是组， 不再是组内的单个数据

```sql
-- 返回分组之后， 每个组中的第一条数据
select * from emp group by post;

set global sql_mode='srict_trans_tables, only_full_group_by' -- 设置之后只能拿到分组数据， 按照什么分组就只能获取分组对应的数据
select * from emp group by post; -- 报错
select post from emp group by post;

-- 分组使用场景(包含关键字 每个、平均、最高、最低)
select post, max(salary) from emp group by post;
select post as '部门', max(salary) as '最高薪资' from emp group by post;

-- 查询分组之后每组的数据 
-- group_concat 获取分组之后每组的数据、拼接操作
select post, group_concat(name) from emp group by post;
select post, group_concat(name,':', salary) from emp group by post;

-- 不分组拼接
select concat('Name: ', name), concat('Salary: ', salary) from emp; -- 显示 Name: zhangsan Salary: 2000

-- 统计每个部门年龄在20岁以上的员工平均薪资
-- 第一步 select * from emp where age > 20;
-- 第二步 select * from emp where age > 20 group by post;
select name, ave(salary) from emp where age > 20 group by post;
```

**注意事项**

关键字where和group by同时出现的时候，group by必须在where之后

Where 筛选条件不能使用聚合函数

```sql
select * from emp where max(salary) > 2000; -- 报错
select name,max(salary) from emp;
```

聚合函数(max\min\avg\count\sum)只能在分组之后使用

### having(分组筛选)

语法和where一致， 但是having可以直接使用聚合函数

```sql
-- 统计各不萌年龄在20岁以上的员工平均工资并且保留平均工资大于 10000 的部门
select name, avg(salary) from emp where age > 20 group by post having avr(salary) > 10000; 
```

### distinct(去重)

**注意事项**
必须是完全一样的数据才可以去重

```sql
select distinct id,age from emp; -- 不能去重
select distinct age from emp;
```

### order by(排序)

```sql
-- 升序(默认)
select * from emp order by salary;

-- 降序
select * from emp order by salary desc;

-- 多个排序
select * from emp order by salary desc,age asc;

-- 统计各不萌年龄在20岁以上的员工平均工资并且保留平均工资大于 1000 的部门，然后对平均工资降序
select name, avg(salary) from emp 
	where age > 20 
	group by post 
	having avr(salary) > 1000
	order by avg(salary);

```

### limit(限制展示条数)

```sql
select * from emp limit 10;

select * from emp limit 1,10; -- 显示从1开始显示10 条数据(1表示起始位置， 10 表示显示条数)
```

### 正则表达式

```sql
select * from emp regexp '^a.*n$'
```

### 联表查询

```sql
-- 基础语法
SELECT 字段列表
    FROM 表1 INNER|LEFT|RIGHT JOIN 表2
    ON 表1.字段 = 表2.字段;

select * from emp, dep where emp.dep_id = dep.id;

-- inner join 内连接  只拼接两张表中有联系的数据
select * from emp inner join dep on emp.dep_id = dep.id;

-- left join  左连接 展示左表中所有数据，没有对应的项就用NULL
select * from emp left join dep on emp.dep_id = dep.id;

-- right join  右连接 展示右表中所有数据，没有对应的项就用NULL
select * from emp right join dep on emp.dep_id = dep.id;

-- union 全连接接 左右两表中的数据全部展示出来
select * from emp union join dep on emp.dep_id = dep.id;
```

### 子查询

将一个查询语句的结果当作另一个查询语句的条件去用
凡是涉及到多表查询的时候都可以使用联表查询和子查询

```sql
-- 查询部门是技术或人力资源的员工信息
-- 1. 先查部门id
-- 2. 筛选员工信息
select * from emp where dep_id in (select id from dep where name='技术' or name='人力资源')

```



## 数据类型

* 数字类型

  | 类型         | 大小                                     | 范围（有符号）                                                                                                                      | 范围（无符号）                                                    | 用途            |
  | :----------- | :--------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------- | :-------------- |
  | TINYINT      | 1 byte                                   | (-128，127)                                                                                                                         | (0，255)                                                          | 小整数值        |
  | SMALLINT     | 2 bytes                                  | (-32 768，32 767)                                                                                                                   | (0，65 535)                                                       | 大整数值        |
  | MEDIUMINT    | 3 bytes                                  | (-8 388 608，8 388 607)                                                                                                             | (0，16 777 215)                                                   | 大整数值        |
  | INT或INTEGER | 4 bytes                                  | (-2 147 483 648，2 147 483 647)                                                                                                     | (0，4 294 967 295)                                                | 大整数值        |
  | BIGINT       | 8 bytes                                  | (-9,223,372,036,854,775,808，9 223 372 036 854 775 807)                                                                             | (0，18 446 744 073 709 551 615)                                   | 极大整数值      |
  | FLOAT        | 4 bytes                                  | (-3.402 823 466 E+38，-1.175 494 351 E-38)，0，(1.175 494 351 E-38，3.402 823 466 351 E+38)                                         | 0，(1.175 494 351 E-38，3.402 823 466 E+38)                       | 单精度 浮点数值 |
  | DOUBLE       | 8 bytes                                  | (-1.797 693 134 862 315 7 E+308，-2.225 073 858 507 201 4 E-308)，0，(2.225 073 858 507 201 4 E-308，1.797 693 134 862 315 7 E+308) | 0，(2.225 073 858 507 201 4 E-308，1.797 693 134 862 315 7 E+308) | 双精度 浮点数值 |
  | DECIMAL      | 对DECIMAL(M,D) ，如果M>D，为M+2否则为D+2 | 依赖于M和D的值                                                                                                                      | 依赖于M和D的值                                                    | 小数值          |

* 字符串

  | 类型       | 大小                  | 用途                            | 注意事项                                                         |
  | :--------- | :-------------------- | :------------------------------ | ---------------------------------------------------------------- |
  | CHAR       | 0-255 bytes           | 定长字符串                      | 只能存储指定长度的字符，不够默认用空格补全， 浪费空间， 存取方便 |
  | VARCHAR    | 0-65535 bytes         | 变长字符串                      | 只能存储指定长度的字符，有几位就存几位， 节省空间                |
  | TINYBLOB   | 0-255 bytes           | 不超过 255 个字符的二进制字符串 |                                                                  |
  | TINYTEXT   | 0-255 bytes           | 短文本字符串                    |                                                                  |
  | BLOB       | 0-65 535 bytes        | 二进制形式的长文本数据          |                                                                  |
  | TEXT       | 0-65 535 bytes        | 长文本数据                      |                                                                  |
  | MEDIUMBLOB | 0-16 777 215 bytes    | 二进制形式的中等长度文本数据    |                                                                  |
  | MEDIUMTEXT | 0-16 777 215 bytes    | 中等长度文本数据                |                                                                  |
  | LONGBLOB   | 0-4 294 967 295 bytes | 二进制形式的极大文本数据        |                                                                  |
  | LONGTEXT   | 0-4 294 967 295 bytes | 极大文本数据                    |                                                                  |

* 枚举(enum)

  ```sql
  create table t1(
  	id int,
  	name varchar(20),
  	sex enum('male', 'female','other') -- 多选一
  )
  ```

  

* 集合(set)

  ```sql
  create table t1(
  	id int,
  	name varchar(20),
  	hobby set('read', 'singing','dancing') -- 多选多
  )
  ```

  

* 时间和日期类型

  | 类型      | 大小 ( bytes) | 范围                                                                                                                              | 格式                |           用途           |
  | :-------- | :------------ | :-------------------------------------------------------------------------------------------------------------------------------- | :------------------ | :----------------------: |
  | DATE      | 3             | 1000-01-01/9999-12-31                                                                                                             | YYYY-MM-DD          |          日期值          |
  | TIME      | 3             | '-838:59:59'/'838:59:59'                                                                                                          | HH:MM:SS            |     时间值或持续时间     |
  | YEAR      | 1             | 1901/2155                                                                                                                         | YYYY                |          年份值          |
  | DATETIME  | 8             | 1000-01-01 00:00:00/9999-12-31 23:59:59                                                                                           | YYYY-MM-DD HH:MM:SS |     混合日期和时间值     |
  | TIMESTAMP | 4             | 1970-01-01 00:00:00/2038结束时间是第 **2147483647** 秒，北京时间 **2038-1-19 11:14:07**，格林尼治时间 2038年1月19日 凌晨 03:14:07 | YYYYMMDD HHMMSS     | 混合日期和时间值，时间戳 |

## 约束条件

表与表之间建立关系的两种方式

1. 通过外键强制建立关系
2. 通过sql语句从逻辑上建立关系 

**类型**

* 非空约束(not null)

* 唯一约束(unique)

* 主键约束(primary key) 
  主键约束除了 not null unique外，还会给表添加索引

  无论是单一主键还是复合主键，一张表主键约束只能有一个(约束只能有一个，但可以作用到好几个字段)

* 外键约束(foreign key)

* 检查约束

* unsigned: 将整形数字设置成无符号

* zerofill: 位数不够用0填充

**外键约束**

​	若有两个表A、B，id是A的主键，而B中也有id字段，则id就是表B的外键，外键约束主要用来维护两个表之间数据的一致性

* 分类
  单一外键: 给一个字段添加外键约束

  复合外键: 给多个字段联合添加一个外键约束

* 一张表中可以有多个外键字段
* **外键注意事项**
  1. 外键值可以为null
  2. 外键字段去引用一张表的某个字段的时候，被引用的字段必须具有unique约束
  3. 有了外键引用之后，表分为父表和子表
  4. 必须先创建父表，再创建子表
  5. 删除数据先删除子表数据
  6. 插入时先插入父表数据

* 级联更新、级联删除

  ```sql
  -- 一对多
  create table dep(
  	id int primary key auto_increment,
    dep_name char(16),
    dep_desc char(32)
  );
  
  
  create table emp(
  	id int primary key auto_increment, 
    name cahr(16),
    gender enum('male', 'female','other') default 'male',
    dep_id int,
    foreign key(dep_id) references dep(id)
    on update cascade  -- 同步更新
    on delete cascade -- 同步删除
  );
  
  -- 多对多
  create table book(
  	id int primary key auto_increment,
    title char(16),
    price float
  );
  
  
  create table author(
  	id int primary key auto_increment, 
    name cahr(16),
    gender enum('male', 'female','other') default 'male',
    age int
  );
  
  
  create table book_author(
  	id int primary key auto_increment, 
    book_id int, 
    author_id int,
    foreign key(book_id) references book(id)
    on update cascade 
    on delete cascade,
    foreign key(author_id) references author(id)
    on update cascade 
    on delete cascade
  );
  
  
  -- 一对一
  -- 外键可以在任意一张表中指定，但是建议建在查询频率比较高的表中
  create table student(
   id int primary key auto_increment,
    name varchar(20), 
    stu_id int,
    foreign key(stu_id) references stuinfo(id)
    on update cascade 
    on delete cascade
  )
  
  create table stuinfo(
  	id int primary key auto_increment,
    age int,
    sex enum('male', 'female','other') default 'male'
  )
  ```

  

**示例**

综合

```sql
create table t1(
	id int primary key, -- 非空且唯一
  name char(20),
  stuId char(16) unique, -- 单列唯一
  -- constraint t_stuid unique(stuId) -- 给约束起名字(方便以后通过这个名字来删除这个约束) constraint是关键字，t_stuid是约束名称 
  ip char(32),
  port int,
  unique(ip, port) -- 联合唯一
);
```

单一主键

```sql
-- 列级定义
create table t_user(
    id int(10) primary key auto_increment, -- 生成自增主键
     name varchar(32)
     );
    
-- 表级定义
create table t_user(
     id int(10),
     name varchar(32) not null,
     constraint t_user_id_pk primary key(id)
    );

```

复合主键

```sql
create table t_user(
     id int(10),
     name varchar(32) not null,
     email varchar(128) unique,
     primary key(id,name)
    );
```



## 视图

* 什么是视图
  视图就是通过查询得到的虚拟表，然后保存下来，下次直接使用

* 为什么要使用视图
  如果要频繁操作一张虚拟表，就可以制作成视图，方便后续直接操作

* 语法

  ```sql
  create view table_name as 虚拟表查询的sql语句;
  
  -- 实例
  create view t as select * from teacher inner join course on where teacher.tid = course.teacher_id;
  ```

  

**注意**

1. 创建的视图在硬盘上只会有表结构， 没有表数据(数据来源于之前查询的表)
2. 视图一般只用来查询， 里面的数据不要继续修改， 可能会影响真正的表

## 触发器

* 什么是触发器
  在满足对表数据进行增、删、改的情况下， 自动触发的功能

* 使用触发器可以帮助我们实现监控、日志

* 语法

  ```sql
  create trigger 触发器名称 before/after insert/update/delete on 表名 for each row 
  begin 
  	sql语句
  end
  
  -- 增
  create trigger trigger_before_t1 before insert on t1 for each row 
  begin 
  	sql语句
  end;
  
  -- 修改默认的结束符
  delimiter $$ -- 将默认结束符修改成$$ 避免造成创建触发器时,执行sql语句出现的';' 和mysql默认的结束符(;)冲突
  ```

  

## 事务

* 什么是事务

  一个最小的不可再分的工作单元；通常一个事务对应一个完整的业务(例如银行账户转账业务，该业务就是一个最小的工作单元)

  一个完整的业务需要批量的DML(insert、update、delete)语句共同联合完成

  事务只和DML语句有关，或者说DML语句才有事务。这个和业务逻辑有关，业务逻辑不同，DML语句的个数不同

  开启一个事物可以包含多条sql，这些sql要么同时成功，要么同时失败，称之为事务的原子性

* 为什么使用
  保证数据操作的安全性

* 事务的特性
  A: 原子性  一个事务是一个不可分割的单位， 事务中包含诸多操作，要么同时成功，要么同时失败
  C: 一致性  事务必须是使数据库从一个一致性的状态变到另一个一致性的状态，和原子性密切相关
  I: 隔离性  一个事务的执行不能被其他的事务干扰
  D: 持久性  一个事务一旦提交成功， 那么它对数据库中数据的修改应该是永久的，接下来的其他操作或者故障不应该对其有任何影响

* 语法

  ```sql
  -- 关键字
  -- 1. 开启事物
  start transaction;
  -- 2. 回滚 恢复事务执行之前的状态
  rollback;
  -- 3. 确认
  commit;
  
  
  create table user(
  id int primary key auto_increment,
  name varchar(20),
  money int
  )
  insert into user(name, money) values ('zhangsan', 1000),('lisi', 1000),('wangwu', 1000)
  
  start transaction;
  update user set money= 1100 where name='lisi';
  update user set money= 900 where name='zhangsan';
  commit;
  
  ```

### 事务隔离级别

1. **未提交读 (READ UNCOMMITTED)**

   一个事务中对数据所做的修改，即使没有提交，这个修改对其他的事务仍是可见的，这种情况下就容易出现脏读，影响了数据的完整性

2. **读提交 (READ COMMITTED)**
   一个事务开始时，只能 “看见” 已经提交的事务所做的修改，一个事务从开始直到提交之前，所做的任何修改对其他事务都是不可见的，也叫不可重复读（nonrepeatable read），有可能出现幻读（Phantom Read），指的是当某个事务在读取某个范围内的记录时，另外一个事务又在该范围内插入了新的记录，当之前的事务再次读取该范围的记录时，会产生幻行（Phantom Row）

3. **可重复读 (REPEATABLE READ)**

   多次读取记录的结果都是一致的，可重复读可以解决上面的不可重复读的情况。但是有这样一种情况，当一个事务在读取某个范围的记录时，另外一个事务在这个范围内插入了一条新的数据，当事务再次进行读取数据时，发现比第一次读取记录多了一条，这就是所谓的幻读，两次读取的结果不一致


   是 MySQL 的默认事务隔离级别，该级别保证了在同一个事物中多次读取同样记录的结果是一致的。解决了脏读，又通过多版本并发控制 mvcc 解决了幻读

4. **可串行 (SERIALIZABLE)**

   串行就像一个队列一个样，每个事务都是排队等候着执行，只有前一个事务提交之后，下一个事务才能进行操作。这种情况虽然可以解决上面的幻读，但是他会在每一条数据上加一个锁，容易导致大量的锁超时和锁竞争，特别不适用在一些高并发的业务场景


## 存储过程

* 语法

  ```sql
  -- 创建
  create procedure pro_name(args1,arg2,...)
  begin 
  	sql
  end
  
  -- 调用
  call pro_name
  
  delimiter $$
  create procedure p1(
  	in m int, -- 不能返回出去
  	in n int,
    out res int, -- 用于返回
  )
  begin
  	select * from student where stid>m and stid<n;
  	set res = 10;
  end$$
  delimiter ;
  
  ```

  

## 函数

## 流程控制

## 常见故障处理方式

1. ERROR 1045 (28000): Access denied for user 'root'@'localhost' (using password: YES)

   **解决方法**

   ```bash
   # 1) 关闭当前mysql服务器
   # 2) 跳过用户名和密码验证
   mysqld --skip-grant-tables
   # 3) 无密码连接
   mysql  
   # 4) 修改密码
   update mysql.user set password=password("password") where user="root";
   # mysql 5.7 设置密码 
   update mysql.user set authentication_string=password('12345678') where user='root';
   # 5) 刷新权限 
   flush privileges;
   # 6) 退出重启mysql登陆
   ```

   

2. ERROR 1820 (HY000): You must reset your password using ALTER USER statement before executing this statement

   **解决方法**

   ```sql
   -- 重新设置密码重新登陆即可
   alter user 'root'@'localhost' identified by 'youpassword';  
   -- 或者
   set password=password("youpassword");
   
   flush privileges;
   ```