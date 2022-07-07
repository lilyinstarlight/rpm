%global bootstrap 0

Name:           python-pymongo
Version:        4.1.1
Release:        1%{?dist}

# All code is ASL 2.0 except bson/time64*.{c,h} which is MIT
License:        ASL 2.0 and MIT
Summary:        Python driver for MongoDB
URL:            https://www.mongodb.com/docs/drivers/pymongo
Source0:        https://github.com/mongodb/mongo-python-driver/archive/%{version}/pymongo-%{version}.tar.gz

BuildRequires: make
BuildRequires:  gcc
%if 0%{!?bootstrap:1}
BuildRequires:  python3-sphinx
%endif
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools

%description
The Python driver for MongoDB.


%package doc
BuildArch: noarch
Summary:   Documentation for python-pymongo

%description doc
Documentation for python-pymongo.


%package -n python3-bson
Summary:        Python bson library
%{?python_provide:%python_provide python3-bson}

%description -n python3-bson
BSON is a binary-encoded serialization of JSON-like documents. BSON is designed
to be lightweight, traversable, and efficient. BSON, like JSON, supports the
embedding of objects and arrays within other objects and arrays.  This package
contains the python3 version of this module.


%package -n python3-pymongo
Summary:        Python driver for MongoDB
Requires:       python3-bson%{?_isa} = %{version}-%{release}
%{?python_provide:%python_provide python3-pymongo}

%description -n python3-pymongo
The Python driver for MongoDB.  This package contains the python3 version of
this module.


%package -n python3-pymongo-gridfs
Summary:        Python GridFS driver for MongoDB
Requires:       python3-pymongo%{?_isa} = %{version}-%{release}
%{?python_provide:%python_provide python3-pymongo-gridfs}

%description -n python3-pymongo-gridfs
GridFS is a storage specification for large objects in MongoDB.  This package
contains the python3 version of this module.


%prep
%setup -q -n mongo-python-driver-%{version}


%build
%py3_build

%if 0%{!?bootstrap:1}
pushd doc
make %{?_smp_mflags} html
popd
%endif


%install
%py3_install
# Fix permissions
chmod 755 %{buildroot}%{python3_sitearch}/bson/*.so
chmod 755 %{buildroot}%{python3_sitearch}/pymongo/*.so


%files doc
%license LICENSE
%if 0%{!?bootstrap:1}
%doc doc/_build/html/*
%endif


%files -n python3-bson
%license LICENSE
%doc README.rst
%{python3_sitearch}/bson


%files -n python3-pymongo
%license LICENSE
%doc README.rst
%{python3_sitearch}/pymongo
%{python3_sitearch}/pymongo-%{version}-*.egg-info


%files -n python3-pymongo-gridfs
%license LICENSE
%doc README.rst
%{python3_sitearch}/gridfs


%changelog
* Thu Jul 07 2022 Lily Foster <lily@lily.flowers> - 4.1.1-1
- Import from Fedora and bump to 4.1.1
