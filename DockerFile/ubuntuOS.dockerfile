FROM ubuntu:22.04
LABEL maintainer='cantahu@163.com'

# 切换到国内aliyun源,更新系统软件包列表并安装必要的软件包
RUN sed -i 's|http://archive.ubuntu.com/ubuntu/|http://mirrors.aliyun.com/ubuntu/|g' /etc/apt/sources.list && \
    sed -i '/^# deb-src /d' /etc/apt/sources.list && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y openssh-server sudo net-tools openjdk-8-jdk && \
    apt-get clean && \
    rm -fr /var/lib/apt/lists/* && \
    # 将sshd配置为在容器启动时自动运行    
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    mkdir /run/sshd && \
    # 初始化ssh的ak/sk,用户后续的ssh免密登录
    ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa && \
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys && \
    rm ~/.ssh/id_rsa.pub

# 设置环境变量指向OpenJDK 8
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# 用命令 sudo passwd root 来获取root权限,更改密码
CMD ["/usr/sbin/sshd", "-D"]
