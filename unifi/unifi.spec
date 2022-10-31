Name:               unifi
Version:            7.2.95
Release:            1%{?dist}
Summary:            UniFi Network Application

License:            Ubiquiti-EULA
URL:                https://www.ui.com/download/unifi/
Source0:            https://dl.ui.com/%{name}/%{version}/UniFi.unix.zip#/UniFi-%{version}.unix.zip
ExclusiveArch:      x86_64 aarch64

BuildRoot:          %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%{?systemd_requires}
BuildRequires:      systemd
BuildRequires:      java-1.8.0-openjdk-headless
Requires:           mongodb-org-server
Requires:           java-1.8.0-openjdk-headless
Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd

%description
A centralized management system for UniFi suite of devices


%global debug_package %{nil}

%define __jar_repack %{nil}


%prep
%setup -q -n UniFi

cat >%{name}.service <<EOF
[Unit]
Description=UniFi Network Application
After=network-online.target

[Service]
Type=simple
User=unifi
Group=unifi
WorkingDirectory=%{_libdir}/%{name}
ExecStart=%{_jvmdir}/jre-1.8.0/bin/java -Dunifi.datadir=%{_sharedstatedir}/%{name} -Dunifi.logdir=%{_localstatedir}/log/%{name} -Dunifi.rundir=%{_rundir}/%{name} -Djava.awt.headless=true -Dfile.encoding=UTF-8 -Dorg.xerial.snappy.tempdir=%{_libdir}/%{name}/tmp -jar %{_libdir}/%{name}/lib/ace.jar start
ExecStop=%{_jvmdir}/jre-1.8.0/bin/java -Dunifi.datadir=%{_sharedstatedir}/%{name} -Dunifi.logdir=%{_localstatedir}/log/%{name} -Dunifi.rundir=%{_rundir}/%{name} -Djava.awt.headless=true -Dfile.encoding=UTF-8 -Dorg.xerial.snappy.tempdir=%{_libdir}/%{name}/tmp -jar %{_libdir}/%{name}/lib/ace.jar stop

[Install]
WantedBy=multi-user.target
EOF

cat >%{name}-tmpfiles.conf <<EOF
d %{_rundir}/%{name} 0755 unifi unifi -
EOF

cat >%{name}-logrotate <<EOF
%{_localstatedir}/log/%{name}/*.log {
    missingok
    notifempty
    copytruncate
    compress
    delaycompress
}
EOF

%build
%{__rm} -r lib/native/{Mac,Windows}
find lib/native/Linux -mindepth 1 -maxdepth 1 -type d | grep -v /%{_arch}'$' | xargs %{__rm} -r

find lib/native -type f -name '*.so' -exec chmod 0755 '{}' ';'

%install
%{__rm} -r %{buildroot}

%{__mkdir} -p %{buildroot}%{_libdir}/%{name}
%{__mkdir} -p %{buildroot}%{_libdir}/%{name}/bin
%{__mkdir} -p %{buildroot}%{_sharedstatedir}/%{name}/{conf,data,tmp,work}
%{__mkdir} -p %{buildroot}%{_localstatedir}/log/%{name}
%{__mkdir} -p %{buildroot}%{_rundir}/%{name}
%{__mkdir} -p %{buildroot}%{_tmpfilesdir}
%{__mkdir} -p %{buildroot}%{_unitdir}

%{__cp} -r dl lib webapps %{buildroot}%{_libdir}/%{name}/

ln -s %{_sharedstatedir}/%{name}/conf %{buildroot}%{_libdir}/%{name}/conf
ln -s %{_sharedstatedir}/%{name}/data %{buildroot}%{_libdir}/%{name}/data
ln -s %{_sharedstatedir}/%{name}/tmp  %{buildroot}%{_libdir}/%{name}/tmp
ln -s %{_sharedstatedir}/%{name}/work %{buildroot}%{_libdir}/%{name}/work

ln -s %{_localstatedir}/log/%{name} %{buildroot}%{_libdir}/%{name}/logs
ln -s %{_rundir}/%{name} %{buildroot}%{_libdir}/%{name}/run

ln -s %{_bindir}/mongod %{buildroot}%{_libdir}/%{name}/bin/mongod

%{__cp} %{name}-tmpfiles.conf %{buildroot}%{_tmpfilesdir}/%{name}.conf
%{__cp} %{name}.service %{buildroot}%{_unitdir}/%{name}.service

%{__mkdir} -p %{buildroot}%{_sysconfdir}/logrotate.d
%{__cp} %{name}-logrotate %{buildroot}%{_sysconfdir}/logrotate.d/%{name}


%files
%attr(-, root, root)   %{_libdir}/%{name}

%attr(-, root, root)   %{_tmpfilesdir}/%{name}.conf
%attr(-, root, root)   %{_unitdir}/%{name}.service

%attr(-, root, root)   %config(noreplace) %{_sysconfdir}/logrotate.d/%{name}

%attr(-, unifi, unifi) %{_localstatedir}/log/%{name}
%attr(-, unifi, unifi) %ghost %{_rundir}/%{name}

%attr(-, unifi, unifi) %config(noreplace) %{_sharedstatedir}/%{name}/conf
%attr(-, unifi, unifi) %config(noreplace) %{_sharedstatedir}/%{name}/data
%attr(-, unifi, unifi) %config(noreplace) %{_sharedstatedir}/%{name}/tmp
%attr(-, unifi, unifi) %config(noreplace) %{_sharedstatedir}/%{name}/work

%doc


%pre
getent group %{name} > /dev/null || groupadd -r %{name}
getent passwd %{name} > /dev/null || useradd -r -g %{name} %{name} -s /sbin/nologin -d %{_sharedstatedir}/%{name}

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service


%changelog
* Wed Sep 29 2021 Lily Foster <lily@lily.flowers> - 6.4.54-1
- Update to follow RPM best practices
