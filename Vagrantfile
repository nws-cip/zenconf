$provision_script = <<PROVISION_SCRIPT
apt-get update
apt-get install -y python-pip python-dev tree git nfs-common portmap vim build-essential
pip install -U setuptools
pip install -U pip virtualenv
PROVISION_SCRIPT

Vagrant.configure("2") do |config|
    config.vm.box = "precise64"
    config.vm.box_url = "http://files.vagrantup.com/precise64.box"

    config.vm.provision "shell", inline: $provision_script
end
