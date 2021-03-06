%global         commit0 5ecfa05a17b505ce642a64fa7453097437bb8a64
%global         shortcommit0 %(c=%{commit0}; echo ${c:0:7})
%global         checkout 20181107git%{shortcommit0}

Name:           storyboard
Version:        0.0.1
Release:        12.%{checkout}%{dist}
Summary:        OpenStack Story Tracking

License:        ASL 2.0
URL:            http://www.openstack.org/
Source0:        https://github.com/openstack-infra/storyboard/archive/%{commit0}.tar.gz
Source1:        storyboard.service
Source2:        storyboard-worker.service
Source3:        wsgi.py
Source10:       logging.conf
Source11:       worker-logging.conf

Patch1:         0001-Add-show-attribute-to-the-Task-model.patch

BuildArch:      noarch

Requires:       python-pbr
Requires:       python-jsonschema
Requires:       python-alembic
Requires:       python-babel
Requires:       python2-iso8601
Requires:       python-oauthlib
Requires:       python2-oslo-config
Requires:       python2-oslo-context
Requires:       python2-oslo-utils
Requires:       python2-pecan
Requires:       python2-oslo-db >= 4.27.0
Requires:       python2-oslo-log
Requires:       python-webob
Requires:       python2-pika
Requires:       python-openid
Requires:       PyYAML
Requires:       python2-requests
Requires:       python-six
Requires:       python-sqlalchemy
Requires:       python2-sqlalchemy-fulltext-search
Requires:       python2-wsme
Requires:       python-migrate
Requires:       python2-stevedore
Requires:       python-tzlocal
Requires:       python2-email
Requires:       python-jinja2
Requires:       python2-PyMySQL
Requires:       python2-APScheduler
Requires:       python-dateutil
Requires:       python2-oslo-concurrency
Requires:       python2-oslo-i18n
Requires:       python-gunicorn
Requires:       wait4service

BuildRequires:  python2-devel
BuildRequires:  python-pbr
BuildRequires:  python-setuptools
BuildRequires:  systemd


%description
Storyboard is a task tracker created to serve the needs of highly-distributed
systems that span multiple projects, to enable cross-project work on a massive
scale.  Concepts were adapted from existing tools, and as many potential points
of contention were removed as possible, to better facilitate coordination of
project work by stakeholders with widely varied interests and needs.


%prep
%autosetup -n %{name}-%{commit0} -p1
rm requirements.txt test-requirements.txt


%build
# Without this file, alembic version aren't built...
touch storyboard/db/migration/alembic_migrations/versions/__init__.py
PBR_VERSION=%{version} %{__python2} setup.py build


%install
PBR_VERSION=%{version} %{__python2} setup.py install --skip-build --root %{buildroot}
rm -R %{buildroot}/usr/etc/
# Install template in place
cp -R storyboard/plugin/email/templates %{buildroot}%{python2_sitelib}/storyboard/plugin/email/
install -p -D -m 0755 %{SOURCE3} %{buildroot}%{python2_sitelib}/storyboard/api/wsgi.py
install -p -D -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/storyboard.service
install -p -D -m 0644 %{SOURCE2} %{buildroot}%{_unitdir}/storyboard-worker.service
install -p -D -m 0644 %{SOURCE10} %{buildroot}%{_sysconfdir}/storyboard/logging.conf
install -p -D -m 0644 %{SOURCE11} %{buildroot}%{_sysconfdir}/storyboard/worker-logging.conf
install -p -D -m 0640 etc/storyboard.conf.sample %{buildroot}%{_sysconfdir}/storyboard/storyboard.conf

install -p -d -m 0700 %{buildroot}%{_sharedstatedir}/storyboard
install -p -d -m 0750 %{buildroot}%{_var}/log/storyboard/
install -p -d -m 0755 %{buildroot}%{_sysconfdir}/sysconfig/
touch %{buildroot}%{_sysconfdir}/sysconfig/storyboard


%pre
getent group storyboard >/dev/null || groupadd -r storyboard
if ! getent passwd storyboard >/dev/null; then
  useradd -r -g storyboard -G storyboard -d %{_sharedstatedir}/storyboard -s /sbin/nologin -c "Storyboard Daemon" storyboard
fi
exit 0


%post
%systemd_post storyboard.service


%preun
%systemd_preun storyboard.service


%postun
%systemd_postun_with_restart storyboard.service


%files
%{_bindir}/storyboard-api
%{_bindir}/storyboard-subscriber
%{_bindir}/storyboard-worker-daemon
%{_bindir}/storyboard-db-manage
%{_bindir}/storyboard-migrate
%{_bindir}/storyboard-cron
%{_unitdir}/storyboard.service
%{_unitdir}/storyboard-worker.service
%config(noreplace) %attr(0644, root, root) %{_sysconfdir}/storyboard/logging.conf
%config(noreplace) %attr(0644, root, root) %{_sysconfdir}/storyboard/worker-logging.conf
%config(noreplace) %attr(0640, root, storyboard) %{_sysconfdir}/storyboard/storyboard.conf
%config(noreplace) %{_sysconfdir}/sysconfig/storyboard
%dir %attr(0750, storyboard, storyboard) %{_sharedstatedir}/storyboard
%dir %attr(0750, storyboard, storyboard) %{_var}/log/storyboard
%{python2_sitelib}/storyboard
%exclude %{python2_sitelib}/storyboard/tests
%{python2_sitelib}/storyboard-*.egg-info


%changelog
* Thu Nov 22 2018 Tristan Cacqueray <tdecacqu@redhat.com> - 0.0.1-12
- Bump version

* Tue Jul 11 2017 Tristan Cacqueray <tdecacqu@redhat.com> - 0.0.1-11
- Backport a couple of fix

* Thu Jun 29 2017 Tristan Cacqueray <tdecacqu@redhat.com> - 0.0.1-10
- Bump version

* Wed May 31 2017 Tristan Cacqueray <tdecacqu@redhat.com> - 0.0.1-9
- Add worker-logging.conf

* Sat May 13 2017 Tristan Cacqueray <tdecacqu@redhat.com> - 0.0.1-8
- Switch to gunicorn

* Wed May 10 2017 Fabien Boucher <fboucher@redhat.com> - 0.0.1-7
- Patch to fix delete responses with body content

* Tue May 09 2017 Fabien Boucher <fboucher@redhat.com> - 0.0.1-6
- Use http plugin and no longer use http-socket

* Fri May 05 2017 Fabien Boucher <fboucher@redhat.com> - 0.0.1-5
- Add the so-keepalive option to uwsgi

* Wed May 03 2017 Fabien Boucher <fboucher@redhat.com> - 0.0.1-4
- Add a WORKERS env var for uwsgi wrapper

* Fri Apr 28 2017 Fabien Boucher <fboucher@redhat.com> - 0.0.1-3
- Bump to last available version this day

* Fri Apr 07 2017 Tristan Cacqueray - 0.0.1-2
- Use wsgi wrapper instead of wsgiref.simple_server

* Tue Mar 14 2017 Tristan Cacqueray - 0.0.1-1
- Initial packaging
