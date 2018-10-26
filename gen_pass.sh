#!/bin/bash

if [ -z $1 ]; then
echo 'enter new password!
example: "$0" 123456
where 123456 - new password'
exit -1
fi

if [ -z $2 ]; then
echo 'enter new password!
example: "$0" 123456
where 123456 - new password'
exit -1
fi

key=`cat ~/.ssh/id_rsa.pub`
#         sdn       mor2     teleo         smol2       smol1      smol3      mor1
array=(10.2.1.207 10.2.1.208 10.2.1.220 10.2.1.201 10.2.1.209 10.2.1.213 10.2.1.214)
for host in ${array[*]}
do
ssh -o StrictHostKeyChecking=no $host 2>/dev/null << EOF
hostname
if [ ! -d  ~/.ssh/ ] ; then
  mkdir ~/.ssh/
  chmod 0700 ~/.ssh/
fi
if [ ! -f "~/.ssh/authorized_keys" ]; then
touch ~/.ssh/authorized_keys
chmod 0600 ~/.ssh/authorized_keys
fi

echo $key > ~/.ssh/authorized_keys
EOF
done






