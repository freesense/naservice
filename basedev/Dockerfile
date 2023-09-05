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
    apt-get install -y g++ gdb && \
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
    conda update -n base -c defaults conda && \
    conda update --channel https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main --all --yes && \
    conda init && \
    \
    #pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple jupyterlab jupyterlab-language-pack-zh-CN && \
    #pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple xeus-python jupyterlab-lsp && \
    #conda install --channel https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main xeus-cling -c conda-forge && \
    #pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple ipydrawio jupyterlab-unfold theme-darcula jupyterlab_code_formatter black isort && \
    #jupyter lab --generate-config && \
    \
    ulimit -c unlimited && \
    apt-get clean && \
    pip3 cache purge && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY /root/ /
