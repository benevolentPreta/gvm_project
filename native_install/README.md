# Install OpenVAS 11 on Ubuntu Server 20.04 script
A script to install Greenbone's OpenVAS 11 (GVM,GSP,GMP) on Ubuntu 20.04 Server\
Tested on iso, and cloud image (last tested on 8-31-2020)\
Please read through script as workarounds are implemented that may not be necessary with future versions\
Also, you shouldn't just install scripts off the internet without at least looking at them;-)\

```
wget https://raw.githubusercontent.com/benevolentpreta/gvm_project/native_install/ubuntu_20.04.sh
vi ubuntu_20.04.sh 
chmod +x ubuntu_20.04.sh
sudo ./ubuntu_20.04.sh 

```

Based on: 
* [Koromicha's install guide](https://kifarunix.com/install-and-setup-gvm-11-on-ubuntu-20-04/)
* [Sumesh MS' install from source guide](https://www.cloudcybersafe.com/greenbone-vulnerability-manager-11-installation-on-ubuntu-from-source/)
