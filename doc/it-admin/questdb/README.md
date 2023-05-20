
## Readme

This [guide](https://questdb.io/docs/get-started/binaries/) explains how to get started with QuestDB using the provided binaries. QuestDB is available as a script called questdb.sh for Linux and FreeBSD, an executable questdb.exe for Windows, and can be installed via Homebrew on macOS.

Before getting started, ensure that you have Java 11 installed on your system. You can check the installed version by running "java -version" command. 

Set the JAVA_HOME environment variable to point to your Java 11 installation folder.

```
export QUESTDB_HOME="/opt/questdb-7.1.3"
export PATH="$QUESTDB_HOME/bin:$PATH"
export JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64"
```

To download the QuestDB binaries, choose the appropriate package for your operating system. For Ubuntu , you can download the questdb-7.1.3-no-jre-bin.tar.gz file. 

Extract the downloaded tarball using the "tar -xvf questdb-7.1.3-no-jre-bin.tar.gz" command.

To run QuestDB, execute the questdb.sh script using "./questdb.sh start".
