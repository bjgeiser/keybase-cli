FROM ubuntu:22.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive
# Build dependencies
RUN apt-get update \
  && apt-get install --no-install-recommends -y \
    git \
    ca-certificates \
    build-essential \
    golang-go \
    wget \
    xz-utils \
    upx

ENV GOPATH=$HOME/gopath
ENV KEYBASE_NO_GUI=1
ENV KEYBASE_SKIP_32_BIT=1

RUN version=v6.2.4 && \
    #wget -qO- https://github.com/keybase/client/releases/download/$version/keybase-$version.tar.xz | xz -d | tar x  && \
    wget --no-check-certificate https://github.com/keybase/client/releases/download/$version/keybase-$version.tar.xz && \
    tar xf keybase-$version.tar.xz && \
    mv client-$version client


RUN  export GOPATH="$HOME/gopath" && \
export PATH="$PATH:$GOPATH/bin" && \
cd client/go && \
go install -ldflags '-w -s' -tags production github.com/keybase/client/go/keybase && \
upx --best --lzma /root/gopath/bin/keybase

RUN  export GOPATH="$HOME/gopath" && \
export PATH="$PATH:$GOPATH/bin" && \
cd client/go && \
go install -ldflags '-w -s' -tags production github.com/keybase/client/go/kbfs/kbfsfuse && \
upx --best --lzma /root/gopath/bin/kbfsfuse

RUN  export GOPATH="$HOME/gopath" && \
export PATH="$PATH:$GOPATH/bin" && \
echo $PWD && \
cd client/go && \
go install -ldflags '-w -s' -tags production github.com/keybase/client/go/kbfs/kbfsgit/git-remote-keybase && \
upx --best --lzma /root/gopath/bin/git-remote-keybase


FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y --no-install-recommends python3 python3-yaml git libc6 && \
    #apt install -y --no-install-recommends python3-yaml && pip install pyyaml && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/gopath/bin/keybase /usr/local/bin
COPY --from=builder /root/gopath/bin/kbfsfuse /usr/local/bin
COPY --from=builder /root/gopath/bin/git-remote-keybase /usr/local/bin
COPY process_commands.py /
COPY startup.sh /
RUN chmod a+x /startup.sh

ENV KEYBASE_RUN_MODE="prod kbfsfuse /keybase"
ENV KEYBASE_NO_GUI=1

ENTRYPOINT ["/startup.sh"]
