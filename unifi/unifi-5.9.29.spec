Name:               unifi
Version:            5.9.29
Release:            1%{?dist}
Summary:            UniFi SDN Controller

License:            Ubiquiti-EULA
URL:                https://www.ubnt.com/download/unifi/
Source0:            https://dl.ubnt.com/%{name}/%{version}/%{name}_sysvinit_all.deb
ExclusiveArch:      x86_64

BuildRoot:          %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%{?systemd_requires}
BuildRequires:      systemd
Requires:           mongodb-server
Requires:           java-1.8.0-openjdk-headless
Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd

%description
UniFi SDN Controller


%define __jar_repack %{nil}


%prep
ar p %{SOURCE0} data.tar.xz | tar xJ

cat >%{name}.service <<EOF
[Unit]
Description=UniFi Controller
After=network-online.target

[Service]
Type=simple
User=unifi
Group=unifi
WorkingDirectory=%{_libdir}/%{name}
ExecStart=%{_bindir}/java -Djava.library.path= -Dorg.xerial.snappy.tempdir=%{_libdir}/%{name}/tmp -jar %{_libdir}/%{name}/lib/ace.jar start
ExecStop=%{_bindir}/java -Djava.library.path= -Dorg.xerial.snappy.tempdir=%{_libdir}/%{name}/tmp -jar %{_libdir}/%{name}/lib/ace.jar stop

[Install]
WantedBy=multi-user.target
EOF

%build
%{__rm} -r usr/lib/%{name}/lib/native/{Mac,Windows,Linux/aarch64,Linux/armv7}

%install
%{__rm} -r %{buildroot}

%{__mkdir} -p %{buildroot}%{_libdir}/%{name}
%{__mkdir} -p %{buildroot}%{_localstatedir}/lib/%{name}/{conf,data,run,tmp,work}
%{__mkdir} -p %{buildroot}%{_localstatedir}/log/%{name}
%{__mkdir} -p %{buildroot}%{_libdir}/%{name}/bin
%{__mkdir} -p %{buildroot}%{_unitdir}

%{__cp} -r usr/lib/%{name}/{dl,lib,webapps} %{buildroot}%{_libdir}/%{name}

ln -s %{_localstatedir}/lib/%{name}/conf %{buildroot}%{_libdir}/%{name}/conf
ln -s %{_localstatedir}/lib/%{name}/data %{buildroot}%{_libdir}/%{name}/data
ln -s %{_localstatedir}/lib/%{name}/run  %{buildroot}%{_libdir}/%{name}/run
ln -s %{_localstatedir}/lib/%{name}/tmp  %{buildroot}%{_libdir}/%{name}/tmp
ln -s %{_localstatedir}/lib/%{name}/work %{buildroot}%{_libdir}/%{name}/work
ln -s %{_localstatedir}/log/%{name}      %{buildroot}%{_libdir}/%{name}/logs

ln -s %{_bindir}/mongod %{buildroot}%{_libdir}/%{name}/bin/mongod
%{__cp} %{name}.service %{buildroot}%{_unitdir}


%files
%attr(-, root, root)   %{_libdir}/%{name}
%attr(-, root, root)   %{_unitdir}/%{name}.service

%attr(-, unifi, unifi) %{_localstatedir}/log/%{name}

%attr(-, unifi, unifi) %config(noreplace) %{_localstatedir}/lib/%{name}/conf
%attr(-, unifi, unifi) %config(noreplace) %{_localstatedir}/lib/%{name}/data
%attr(-, unifi, unifi) %config(noreplace) %{_localstatedir}/lib/%{name}/run
%attr(-, unifi, unifi) %config(noreplace) %{_localstatedir}/lib/%{name}/tmp
%attr(-, unifi, unifi) %config(noreplace) %{_localstatedir}/lib/%{name}/work

%doc


%pre
getent group %{name} > /dev/null || groupadd -r %{name}
getent passwd %{name} > /dev/null || useradd -r -g %{name} %{name} -s /sbin/nologin -d %{_localstatedir}/lib/%{name}

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service


%changelog
