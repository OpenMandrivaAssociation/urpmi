##################################################################
#
#
# !!!!!!!! WARNING => THIS HAS TO BE EDITED IN THE CVS !!!!!!!!!!!
#
#
##################################################################

# local RH-friendly definition of %mkrel, so we can assume it works and drop 
# other release hacking macros
%{?!mkrel: %define mkrel(c:) %{-c: 0.%{-c*}.}%{1}%{?distsuffix:.%distsuffix}%{?distversion}}
%{?!makeinstall_std: %define makeinstall_std() make DESTDIR=%{?buildroot:%{buildroot}} install}

%define name	urpmi
%define version	4.9.27
%define release	%mkrel 1

%define group %(perl -e 'print "%_vendor" =~ /\\bmandr/i ? "System/Configuration/Packaging" : "System Environment/Base"')

%define compat_perl_vendorlib %(perl -MConfig -e 'print "%{?perl_vendorlib:1}" ? "%{perl_vendorlib}" : "$Config{installvendorlib}"')
%global allow_gurpmi %(perl -e 'print "%_vendor" =~ /\\bmandr/i ? 1 : 0')
%define req_webfetch %(perl -e 'print "%_vendor" =~ /\\bmandr/i ? "webfetch" : "curl wget"')
%{?!_sys_macros_dir: %global _sys_macros_dir /etc/rpm}

Name:		%{name}
Version:	%{version}
Release:	%{release}
Group:		%{group}
License:	GPL
Source0:	%{name}-%{version}.tar.bz2
Summary:	Command-line software installation tools
URL:		http://search.cpan.org/dist/%{name}/
Requires:	%{req_webfetch} eject gnupg
Requires(post):	perl-Locale-gettext >= 1.05-4mdv
Requires(post):	perl-URPM >= 1.63
# gzip is used in perl-URPM for synthesis and hdlist
Requires(post):	gzip
#- this one is require'd by urpmq, so it's not found [yet] by perl.req
Requires:	perl-MDV-Packdrakeng >= 1.01
BuildRequires:	bzip2-devel
BuildRequires:	gettext
BuildRequires:	perl
BuildRequires:	perl-File-Slurp
BuildRequires:	perl(Net::LDAP)
BuildRequires:	perl-URPM >= 1.63
BuildRequires:	perl-MDV-Packdrakeng
BuildRequires:	perl-MDV-Distribconf
BuildRequires:	perl-Locale-gettext >= 1.05-4mdv
# for genhdlist in make test:
BuildRequires:  rpmtools
BuildRequires:  ash
BuildRequires:  perl-Expect
BuildRoot:	%{_tmppath}/%{name}-buildroot
BuildArch:	noarch
Conflicts:	man-pages-fr < 1.58.0-8mdk
Conflicts:	rpmdrake < 3.19
Conflicts:	curl < 7.13.0
Conflicts:	wget < 1.10.2-6mdv2008.0
Conflicts:	mandrake-mime

%description
urpmi is Mandriva Linux's console-based software installation tool. You can
use it to install software from the console in the same way as you use the
graphical Install Software tool (rpmdrake) to install software from the
desktop. urpmi will follow package dependencies -- in other words, it will
install all the other software required by the software you ask it to
install -- and it's capable of obtaining packages from a variety of media,
including the Mandriva Linux installation CD-ROMs, your local hard disk,
and remote sources such as web or FTP sites.

%if %{allow_gurpmi}
%package -n gurpmi
Summary:	User mode rpm GUI install
Group:		%{group}
Requires:	urpmi >= %{version}-%{release}
Requires:	usermode usermode-consoleonly
Obsoletes:	grpmi
Provides:	grpmi
Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils

%description -n gurpmi
gurpmi is a graphical front-end to urpmi.
%endif

%package -n urpmi-parallel-ka-run
Summary:	Parallel extensions to urpmi using ka-run
Requires:	urpmi >= %{version}-%{release}
Requires:	parallel-tools
Group:		%{group}

%description -n urpmi-parallel-ka-run
urpmi-parallel-ka-run is an extension module to urpmi for handling
distributed installation using ka-run or Taktuk tools.

%package -n urpmi-parallel-ssh
Summary:	Parallel extensions to urpmi using ssh and scp
Requires:	urpmi >= %{version}-%{release} openssh-clients perl
Group:		%{group}

%description -n urpmi-parallel-ssh
urpmi-parallel-ssh is an extension module to urpmi for handling
distributed installation using ssh and scp tools.

%package -n urpmi-ldap
Summary:	Extension to urpmi to specify media configuration via LDAP
Requires:	urpmi >= %{version}-%{release}
Requires:	openldap-clients
Group:		%{group}

%description -n urpmi-ldap
urpmi-ldap is an extension module to urpmi to allow to specify
urpmi configuration (notably media) in an LDAP directory.

%package -n urpmi-recover
Summary:	A tool to manage rpm repackaging and rollback
Requires:	urpmi >= %{version}-%{release}
Requires:	perl
Requires:	perl-DateManip
Group:		%{group}

%description -n urpmi-recover
urpmi-recover is a tool that enables to set up a policy to keep trace of all
packages that are uninstalled or upgraded on an rpm-based system, and to
perform rollbacks, that is, to revert the system back to a previous state.

%prep
%setup -q -n %{name}-%{version}

%build
%{__perl} Makefile.PL INSTALLDIRS=vendor \
%if %{allow_gurpmi}
    --install-gui \
%endif
    --install-po
%{__make}

%check
%{__make} test

%install
%{__rm} -rf %{buildroot}
%{makeinstall_std}

# bash completion
install -d -m 755 %{buildroot}%{_sysconfdir}/bash_completion.d
install -m 644 %{name}.bash-completion %{buildroot}%{_sysconfdir}/bash_completion.d/%{name}

# rpm-find-leaves is invoked by this name in rpmdrake
( cd %{buildroot}%{_bindir} ; ln -s -f rpm-find-leaves urpmi_rpm-find-leaves )

# Don't install READMEs twice
rm -f %{buildroot}%{compat_perl_vendorlib}/urpm/README*

# For ghost file
mkdir -p %{buildroot}%{_sys_macros_dir}
touch %{buildroot}%{_sys_macros_dir}/urpmi.recover.macros

# Desktop entry (only used to register new MIME type handler, so no icon etc.)
%if %{allow_gurpmi}
mkdir -p %buildroot%_datadir/applications
cat > %buildroot%_datadir/applications/mandriva-gurpmi.desktop << EOF
[Desktop Entry]
Name=Software Installer
Comment=Graphical front end to install RPM files
Exec=%{_bindir}/gurpmi %%F
Terminal=false
Type=Application
StartupNotify=true
Categories=GTK;X-MandrivaLinux-.hidden
MimeType=application/x-rpm;application/x-urpmi;
EOF
%endif

mkdir -p %buildroot%_datadir/mimelnk/application
cat > %buildroot%_datadir/mimelnk/application/x-urpmi.desktop << EOF
[Desktop Entry]
Type=MimeType
Comment=urpmi file
MimeType=application/x-urpmi
Patterns=*.urpmi;
EOF

mkdir -p %buildroot%_datadir/mime/packages
cat > %buildroot%_datadir/mime/packages/gurpmi.xml << EOF
<?xml version="1.0"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
  <mime-type type="application/x-urpmi">
    <comment>urpmi file</comment>
    <glob pattern="*.urpmi"/>
  </mime-type>
</mime-info>
EOF

%find_lang %{name}

%clean
%{__rm} -rf %{buildroot}

%preun
if [ "$1" = "0" ]; then
  cd /var/lib/urpmi
  rm -f compss provides depslist* descriptions.* *.cache hdlist.* synthesis.hdlist.* list.*
  cd /var/cache/urpmi
  rm -rf partial/* headers/* rpms/*
fi
exit 0

%post -p /usr/bin/perl
use urpm::media;
if (-e "/etc/urpmi/urpmi.cfg") {
    $urpm = new urpm;
    urpm::media::read_config($urpm);
    urpm::media::update_media($urpm, nolock => 1, nopubkey => 1);
}

%if %{allow_gurpmi}
%post -n gurpmi
%{update_menus}
%{update_desktop_database}
%{update_mime_database}

%postun -n gurpmi
%{clean_menus}
%{clean_desktop_database}
%{clean_mime_database}
%endif

%files -f %{name}.lang
%defattr(-,root,root)
%dir /etc/urpmi
%dir /var/lib/urpmi
%dir /var/cache/urpmi
%dir /var/cache/urpmi/partial
%dir /var/cache/urpmi/headers
%dir /var/cache/urpmi/rpms
%config(noreplace) /etc/urpmi/skip.list
%config(noreplace) /etc/urpmi/inst.list
%config(noreplace) %{_sysconfdir}/bash_completion.d/%{name}
%{_bindir}/urpmi_rpm-find-leaves
%{_bindir}/rpm-find-leaves
%{_bindir}/urpmf
%{_bindir}/urpmq
%{_sbindir}/urpmi
%{_sbindir}/rurpmi
%{_sbindir}/rurpme
%{_sbindir}/urpme
%{_sbindir}/urpmi.addmedia
%{_sbindir}/urpmi.removemedia
%{_sbindir}/urpmi.update
%{_mandir}/man3/urpm*
%{_mandir}/man5/urpm*
%{_mandir}/man5/proxy*
%{_mandir}/man8/rurpm*
%{_mandir}/man8/urpme*
%{_mandir}/man8/urpmf*
%{_mandir}/man8/urpmq*
%{_mandir}/man8/urpmi.8*
%{_mandir}/man8/urpmi.addmedia*
%{_mandir}/man8/urpmi.removemedia*
%{_mandir}/man8/urpmi.update*
%{_mandir}/man8/urpmihowto*
%lang(fr) %{_mandir}/fr/man?/urpm*
%dir %{compat_perl_vendorlib}/urpm
%{compat_perl_vendorlib}/urpm.pm
%{compat_perl_vendorlib}/urpm/args.pm
%{compat_perl_vendorlib}/urpm/bug_report.pm
%{compat_perl_vendorlib}/urpm/cfg.pm
%{compat_perl_vendorlib}/urpm/download.pm
%{compat_perl_vendorlib}/urpm/get_pkgs.pm
%{compat_perl_vendorlib}/urpm/install.pm
%{compat_perl_vendorlib}/urpm/lock.pm
%{compat_perl_vendorlib}/urpm/md5sum.pm
%{compat_perl_vendorlib}/urpm/media.pm
%{compat_perl_vendorlib}/urpm/msg.pm
%{compat_perl_vendorlib}/urpm/parallel.pm
%{compat_perl_vendorlib}/urpm/prompt.pm
%{compat_perl_vendorlib}/urpm/removable.pm
%{compat_perl_vendorlib}/urpm/select.pm
%{compat_perl_vendorlib}/urpm/signature.pm
%{compat_perl_vendorlib}/urpm/sys.pm
%{compat_perl_vendorlib}/urpm/util.pm
%doc NEWS

%if %{allow_gurpmi}
%files -n gurpmi
%defattr(-,root,root)
%{_bindir}/gurpmi
%{_bindir}/gurpmi2
%{_sbindir}/gurpmi2
%{_datadir}/applications/mandriva-gurpmi.desktop
%{_datadir}/mimelnk/application/x-urpmi.desktop
%{_datadir}/mime/packages/gurpmi.xml
%{compat_perl_vendorlib}/gurpmi.pm
%endif

%files -n urpmi-parallel-ka-run
%defattr(-,root,root)
%doc urpm/README.ka-run
%dir %{compat_perl_vendorlib}/urpm
%{compat_perl_vendorlib}/urpm/parallel_ka_run.pm

%files -n urpmi-parallel-ssh
%defattr(-,root,root)
%doc urpm/README.ssh
%dir %{compat_perl_vendorlib}/urpm
%{compat_perl_vendorlib}/urpm/parallel_ssh.pm

%files -n urpmi-ldap
%doc urpmi.schema
%{compat_perl_vendorlib}/urpm/ldap.pm

%files -n urpmi-recover
%{_sbindir}/urpmi.recover
%{_mandir}/man8/urpmi.recover*
%config(noreplace) %_sys_macros_dir/urpmi.recover.macros
%ghost %_sys_macros_dir/urpmi.recover.macros


