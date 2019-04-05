FROM quay.io/pypa/manylinux1_x86_64

RUN useradd tiledb
RUN mkdir /home/tiledb
ENV /home/tiledb

RUN cd /tmp &&
  /opt/python/cp27-cp27m/bin/pip install cmake && \
  curl -L https://install.perlbrew.pl | bash && \
  source $HOME/perl5/perlbrew/etc/bashrc && \
  perlbrew --notest install perl-5.10.0 && \
  perlbrew use perl-5.10.0 && \
  yum install -y zlib-devel

ENV CMAKE=/opt/python/cp27-cp27m/bin/cmake 

# build libtiledb (core)
# notes:
#    1) we are using auditwheel from https://github.com/pypa/auditwheel
#       this verifies and tags wheel products with the manylinux1 label,
#       and allows us to build libtiledb once, install it to a normal
#       system path, and then use it to build wheels for all of the python
#       versions.
#    2) perl-5.10.0, buit above, is required to build OpenSSL
RUN cd /home/tiledb/ && \
  perlbrew use perl-5.10.0 && \
  git clone https://github.com/TileDB-Inc/TileDB && \
  mkdir build && \
  cd build && \
  $CMAKE -DTILEDB_S3=ON -DTILEDB_HDFS=ON -DTILEDB_TESTS=OFF -DTILEDB_FORCE_ALL_DEPS:BOOL=ON ../TileDB && \
  make -j2 && make check && \
  make install-tiledb

# build python27 wheel
RUN cd /home/tiledb/TileDB-Py && \
  /opt/python/cp27-cp27m/bin/python2.7 setup.py build_ext bdist_wheel
