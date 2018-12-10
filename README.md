# KPI

Fix pip intall MYSQL-python:

- nano /usr/local/bin/mysql_config
- Change these lines:
    from:
        libs="-L$pkglibdir"
        libs="$libs  -l"
    to:
        libs="-L$pkglibdir"
        libs="$libs  -lmysqlclient -lssl -lcrypto"
- xcode-select --install
- brew install openssl
- export LIBRARY_PATH=$LIBRARY_PATH:/usr/local/opt/openssl/lib/