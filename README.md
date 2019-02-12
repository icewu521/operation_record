# operation_record
operation record system


笔者在工作中经常遇到一个工作需要大家配合协调或者个人的工作内容会影响整个团队的问题，这时及时记录与分享个人的工作就显得尤为重要。也许你可以微信、QQ建个群，大家共享，但有些消息太多遗漏了，甚至有些内部资料进度不便走公网，那怎么办呢？利用Linux以及Python打造一个属于我们自己的记录与分享系统，随时存取我们需要分享的信息，通过授权可以分享给需要的人员，运行在私网环境，安全可靠.
   
平台及软件使用的是Linux+Python+MySQL。此外，使用的Python扩展包有Tornado+pymysql+hashlib+time+psutil+json，以上程序软件全部为开源免费软件。开发环境使用PyCharm。

项目目录中,database.py是连接数据库的驱动文件,包括连接方式口令,定义好的数据库操作函数等.
operation_record.py是项目的主文件在windows下编写.linux_operation_record.py是通过screen.txt文件中sed命令转化为linux下的可执行文件.别忘了执行添加权限命令chmod + x

1 安装操作系统等基础环境。Linux笔者选用的是CentOS 7.1 x64版本，其它版本也可，根据自己喜好决定。应用软件Python下载于官网，编译安装即可，需要注意的是Python 2版本与3版本差距较大，笔者基于Python 3.6版本开发。数据库使用MySQL 5.7.20版本，下载与操作系统对应的rpm包安装。Tornado是基于Python的Web开发框架，它是非阻塞式服务器，性能强大，笔者选用的4.5.2版本，使用命令pip install tornado安装即可。

2 数据库设计。数据库表结构,建表等语句,参考createtables.txt。笔者设计了三张表，一张用于存储主要信息记录的表T_CONTENT；一张存储用户的表T_USER，用于存储用户的账户、密码、权限等；还有一张表T_SETTING用于存储系统设置等。可以直接写SQL语句在数据库中执行建表，也可以在诸如Navicat之类的客户端程序中可视化建表。表中的字段也是根据业务需要而设置。
 
3 构建框架，建立Web服务。我们可以使用Tornado快速搭建一个WEB服务器，为我们的系统提供Web服务框架。其中，application是指每个子应用功能，由于他们是由不同的URL组成的，当浏览器访问不同的URL，对应application中不同的处理子程序方法的入口，从而进入子程序处理。它的多少取决于业务的需要。当然我们还要设置一些诸如模板目录、cookies设置、根目录等参数。
 
4 创建HTML渲染模板。Tornado可以基于模板使用render方法渲染出HTML代码返回给浏览器，呈现在用户面前。所有用户需要操作的和返回的内容均要在此预先定义模板，在程序运行时根据业务流程动态生成用户需要的数据，渲染为HTML代码返回给浏览器。这里就需要仔细思考业务的流程以及页面样式。此处HTML模板全部位于项目根目录下的templates目录下。
 
6 后台管理与其它。系统在上线运行后同样需要维护，比如设置每页显示的条目数、提交数据错误如何更正、密码忘记的重置、用户权限的授权与查看、磁盘与系统状况等等。这些问题的处理不能仅由管理员进入数据库通过命令操作，否则这将是一个巨大的工作量，同时也存在安全隐患。这里通过权限管理，同步设计了管理员后台维护页面，这样管理员同样通过Web页面的方式即可管理系统绝大多数的运行情况。
 
    数据会每天随着用户的不断提交而增大，上线后需要不定期关注磁盘的使用情况。笔者实验环境中数据目录在根目录下，故只监控了一个根目录，也可以根据情况设置监控多个目录。笔者后台磁盘监控使用了ajax异步更新机制，每十秒自动更新一次数据，磁盘已用占比用饼状图显示.
 
此套系统已在笔者实验环境中稳定运行一年两个月，稳定可靠。但还有一些不足之处，如不能添加图片、视频、文件的共享，还有不断完善的空间，这里抛砖引玉，有兴趣可以再完善。




