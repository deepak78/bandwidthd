# You can compile this without sqlite support by running:
# rpmbuild -ba bandwidthd.spec --without sqlite --with pgsql
%bcond_with pgsql
%bcond_without sqlite

Name:           bandwidthd
Version:        2.0.1
Release:        32%{?dist}
Summary:        Tracks network usage and builds html and graphs

Group:          System Environment/Daemons
License:        GPL+
URL:            http://bandwidthd.sourceforge.net/
Source0:        %{name}-%{version}.tar.gz
Source1:        %{name}
Source2:        %{name}.service
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  autoconf, gd-devel, libpng-devel, bison, flex
%if %{with pgsql}
BuildRequires: postgresql-devel
%endif
%if %{with sqlite}
BuildRequires: sqlite-devel
%endif
%if "0%{?dist}" == "0.el4"
BuildRequires:  libpcap
%else
BuildRequires:  libpcap-devel
%endif
%if 0%{?fedora} || 0%{?rhel} > 6
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
BuildRequires: systemd-units
%else
Requires(post): /sbin/chkconfig
Requires(preun):/sbin/chkconfig
Requires(preun):/sbin/service
%endif

%description
Bandwidthd is a UNIX daemon/Windows service for graphing the traffic
generated by each machine on several configurable subnets.  It is much
easier to configure than MRTG, and provides significantly more useful
information.  MRTG only tells you how much bandwidth you are using,
Bandwidthd tells you that, and who is using it.

Each IP address that has moved any significant volume of traffic has its
own graph.  The graphs are color coded to help you figure out at a glance
if your user is surfing the web, or surfing Kazaa.

Bandwidthd is targeted to run on my routing platforms.  It is very low
overhead.  Easily graphing small business traffic on a 133Mhz Elan 486
every 2.5 minutes. My entire ISP (2000-3000 IP addresses across 4 states)
is graphed on a Celeron 450 every 10 minutes.


%prep
%setup -q

%build
cp -avf /usr/lib/rpm/config.{sub,guess} .
autoheader
autoconf
%configure --prefix=%{_prefix} \
  --exec-prefix=%{_prefix} \
  --sysconfdir=%{_sysconfdir} \
  --bindir=%{_bindir} \
  --datadir=%{_var}/www
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
# start script
%if 0%{?fedora} || 0%{?rhel} > 6
mkdir -p $RPM_BUILD_ROOT%{_unitdir}
install -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_unitdir}/
%else
install -d $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/
%endif
# install apache configuration
install -d $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d
install -m 0644 -T httpd.conf $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/%{name}.conf
install -m 0755 -d $RPM_BUILD_ROOT%{_datarootdir}/%{name}
install -m 0644 -t $RPM_BUILD_ROOT%{_datarootdir}/%{name} phphtdocs/*.* phphtdocs/.htaccess

%clean
rm -rf $RPM_BUILD_ROOT


%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%defattr(-,root,root,-)
%doc README CHANGELOG TODO schema.postgresql
%config(noreplace) %{_sysconfdir}/%{name}.conf
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%if 0%{?fedora} || 0%{?rhel} > 6
%{_unitdir}/%{name}.service
%else
%attr(755,root,root) %{_sysconfdir}/rc.d/init.d/%{name}
%endif
%{_sbindir}/%{name}
%dir %{_var}/www/%{name}
%{_var}/www/%{name}/*
%{_datarootdir}/%{name}

%changelog
* Thu Jul 28 2016 Davide Principi <davide.principi@nethesis.it> - 2.0.1-32
- Added sqlite output support from sources on SF CVS bandwidthd repo
- Build for NethServer
- Merged patch files into git repository

* Wed Feb 03 2016 Ján ONDREJ (SAL) <ondrejj(at)salstar.sk> - 2.0.1-31
- Fix bandwidthd.service file permissions and patch URL.

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.1-30
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jun 17 2015 Ján ONDREJ (SAL) <ondrejj(at)salstar.sk> - 2.0.1-29
- GCC5 inline compatibility.

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.1-28
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Aug 15 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.1-27
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.1-26
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri Jan 10 2014 Ján ONDREJ (SAL) <ondrejj(at)salstar.sk> - 2.0.1-25
- Scriptlets replaced with new systemd macros (#850042)
  Thanks to Václav Pavlín.

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.1-24
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Jun 11 2013 Remi Collet <rcollet@redhat.com> - 2.0.1-23
- rebuild for new GD 2.1.0

* Sat Mar 23 2013 Ján ONDREJ (SAL) <ondrejj(at)salstar.sk> - 2.0.1-22
- added autoreconf to prep section (bz#925079)

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.1-21
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.1-20
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.1-19
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Nov 17 2011 Ján ONDREJ (SAL) <ondrejj(at)salstar.sk> - 2.0.1-18
- systemd pre/post scripts

* Wed Nov 16 2011 Ján ONDREJ (SAL) <ondrejj(at)salstar.sk> - 2.0.1-17
- added native systemd service (bz#754478)

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.1-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Dec 09 2009 Ján ONDREJ (SAL) <ondrejj(at)salstar.sk> - 2.0.1-15
- Applied patch from lkundrak to do not hang when no devices found. bz#537073

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.1-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.1-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Dec 13 2008 Jan ONDREJ (SAL) <ondrejj(at)salstar.sk> - 2.0.1-11
- updated config.sub and config.guess to build on ppc64
- added libpng-devel again (required for EPEL-4)

* Sat Dec 13 2008 Jan ONDREJ (SAL) <ondrejj(at)salstar.sk> - 2.0.1-8
- removed dependency on gd
- removed one line of autoconf
- removed dependency on libpng-devel
- phphtdocs added for pgsql build, execute bit for gif and sh removed

* Mon Dec 8 2008 Jan ONDREJ (SAL) <ondrejj(at)salstar.sk> - 2.0.1-7
- changed License to GPL+

* Mon Dec 8 2008 Jan ONDREJ (SAL) <ondrejj(at)salstar.sk> - 2.0.1-6
- buildroot macro replaced by RPM_BUILD_ROOT variable
- added autoconf into build-requires
- by default compiled with postgresql support
- conditional build without postgresql (--without pgsql)
- libpng removed from requires

* Mon Dec 8 2008 Jan ONDREJ (SAL) <ondrejj(at)salstar.sk> - 2.0.1-5
- conditional build for el4

* Sun Sep 9 2007 Jan ONDREJ (SAL) <ondrejj(at)salstar.sk> - 2.0.1-4
- updated license and summary
- changed init script permissions

* Tue Mar 13 2007 Jan ONDREJ (SAL) <ondrejj(at)salstar.sk>
- updated from version by Michal Ambroz <rebus@seznam.cz>
- added apache configuration script
- moved into /var/www/bandwidthd
- spec file name typo fixed
