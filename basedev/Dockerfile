FROM lscr.io/linuxserver/code-server

ENV USER freesense
ENV EMAIL freesense@126.com
ENV PATH="/opt/miniconda/bin:${PATH}"

RUN rm /etc/dpkg/dpkg.cfg.d/excludes && \
    cp /etc/apt/sources.list /etc/apt/sources.list.bak && \
    sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list && \
    sed -i s@/security.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list && \
    apt-get update && apt-get upgrade -y && \
    \
    #dpkg -l | grep ^ii | cut -d' ' -f3 | xargs apt-get install -y --reinstall && \     # 没必要把现有包全部重新安装一遍
    apt-get install -y man wget language-pack-zh-hans language-pack-zh-hans-base && \
    \
    apt-get install -y g++ && \
    apt-get install -y autoconf automake libtool build-essential && \
    \
    wget ftp://gcc.gnu.org/pub/gcc/libstdc++/doxygen/libstdc++-man.4.4.0.tar.bz2 && \
    tar -jxvf libstdc++-man.4.4.0.tar.bz2 && \
    cp libstdc++-man-4.4.0/man3/* /usr/share/man/man3/ && \
    rm -rf libstdc++-man* && \
    \
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    chmod +x ~/miniconda.sh && \
    ~/miniconda.sh -p /opt/miniconda -b && \
    rm -f ~/miniconda.sh && \
    conda update --all --yes && \
    conda init && \
    conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/ && \
    conda config --set show_channel_urls yes && \
    pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set install.trusted-host mirrors.aliyun.com && \
    \
    ulimit -c unlimited && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
