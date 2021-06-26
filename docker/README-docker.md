The dockerized version of the script simplifies deployment by bundling the script and its associated requirements in a container.

To use the container, populate a directory with script config files then bind mount that directory into the container at /config. E.g., if config files are located at /home/user/config, specify "--volume /home/user/config:/config" to the docner run command.

To run the performance script using a specific cofiguration file, specify the script location relative to the /config location within the container. E.g., for a confg file named renc-rr1.json with the /home/user/conf directory specify /config/renc-rr1.json to the docker run command. A full command would look like:

    docker run --rm --volume /home/user/config:/config /config/renc-rr1.json

The docker directory also contains a utility script, run.sh, which will execute the container once per configuration file (i.e. with a configuration directory containing multiple config files for multiple hosts)



