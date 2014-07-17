# MODIFY GREP REGEX TO MATCH YOUR SERVERS

for i in `sl vs list | grep -E "\.jumpgate\.com" | cut -d ' ' -f 1`; do sl vs cancel -y $i; done
