#!/bin/sh

# add gvmuser and alias for executing gvm-script commands inside a docker container

groupadd -g 999 gvmuser
useradd -r -u 999 -s /bin/bash -g gvmuser gvmuser
echo 'alias gs="gvm-script --gmp-username ${USERNAME} --gmp-password ${PASSWORD} tls"' >> /etc/bash.bashrc