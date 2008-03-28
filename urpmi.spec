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
%define version	5.17
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
URL:		http://wiki.mandriva.com/en/Tools/urpmi
Requires:	%{req_webfetch} eject gnupg
Requires(post):	perl-Locale-gettext >= 1.05-4mdv
Requires(post):	perl-URPM >= 3.10
# gzip is used in perl-URPM for synthesis and hdlist
Requires(post):	gzip
Requires:	genhdlist2
Requires:	perl-Time-ZoneInfo >= 0.3.4
Requires:	meta-task
Suggests:	perl-Hal-Cdroms
BuildRequires:	bzip2-devel
BuildRequires:	gettext
BuildRequires:	perl
BuildRequires:	perl-File-Slurp
BuildRequires:	perl(Net::LDAP)
BuildRequires:	perl-URPM >= 1.76
BuildRequires:	perl-MDV-Packdrakeng
BuildRequires:	perl-MDV-Distribconf
BuildRequires:	perl-Locale-gettext >= 1.05-4mdv
# for make test:
BuildRequires:	perl-Test-Pod
BuildRequires:	perl-XML-LibXML
# for genhdlist in make test:
BuildRequires:  rpmtools
BuildRequires:  dash-static
BuildRequires:  perl-Expect
BuildRoot:	%{_tmppath}/%{name}-buildroot
BuildArch:	noarch
Conflicts:	man-pages-fr < 1.58.0-8mdk
Conflicts:	rpmdrake < 3.19
Conflicts:	curl < 7.13.0
Conflicts:	wget < 1.10.2-6mdv2008.0
# ugly workaround for upgrading 2007.0:
Provides:	mandrake-mime = 0.5
Obsoletes:	mandrake-mime < 0.5

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
Requires:	perl(Date::Manip)
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
Categories=GTK;X-MandrivaLinux-.hidden;
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

%triggerprein -- urpmi < 4.10.19
# (it should be on perl-URPM < 3.03, because urpmi will be upgraded after perl-URPM)
#
# old urpmi+perl-URPM may have generated synthesis from hdlist.
# we must regenerate synthesis again to have suggests in it.
if [ -d /var/lib/urpmi ]; then
   cd /var/lib/urpmi
   for i in hdlist*.cz; do 
      if [ -e "synthesis.$i" ]; then
        echo "forcing synthesis.$i to be regenerated"	
        rm "synthesis.$i"
	need_rebuild=1
      fi
   done
   if [ -n "$need_rebuild" ]; then
      # nb: this script is using old urpmi (ie urpmi <= 4.10.14)
      # which still knows how to generate synthesis from hdlist
      perl <<"EOF"
if (-e "/etc/urpmi/urpmi.cfg") {
    require urpm;
    $urpm = urpm->new;

    # use inlined media/media_info/file-deps.
    # This ensures a second pass is not needed, 
    # esp since old urpmi code doesn't rebuild synthesis when it should
    foreach (<DATA>) {
	chomp;
        $urpm->{provides}{$_} = undef;
    }   
    # do not let $urpm->clean drop what we did above
    undef *urpm::clean; *urpm::clean = sub {};

    if (eval { require urpm::media; 1 }) {
        urpm::media::read_config($urpm);
        urpm::media::update_media($urpm, nolock => 1, nopubkey => 1);
    } else {
        urpm::read_config($urpm);
        urpm::update_media($urpm, nolock => 1, nopubkey => 1);
    }
}

__DATA__
/bin/awk
/bin/bash
/bin/cp
/bin/csh
/bin/egrep
/bin/gawk
/bin/grep
/bin/ksh
/bin/ln
/bin/rm
/bin/sed
/bin/sh
/bin/tcsh
/etc/init.d
/etc/rc.d/init.d
/etc/sgml
/etc/vservers
/sbin/chkconfig
/sbin/fuser
/sbin/install-info
/sbin/ip
/sbin/ldconfig
/sbin/service
/usr/bin/ar
/usr/bin/chattr
/usr/bin/cmp
/usr/bin/cw
/usr/bin/env
/usr/bin/expect
/usr/bin/fontforge
/usr/bin/gbx
/usr/bin/gconftool-2
/usr/bin/gtk-query-immodules-2.0
/usr/bin/guile
/usr/bin/irssi
/usr/bin/ksh
/usr/bin/ksi
/usr/bin/ld
/usr/bin/ldd
/usr/bin/mktexlsr
/usr/bin/moin-changePage
/usr/bin/objdump
/usr/bin/openssl
/usr/bin/pbs_wish
/usr/bin/perl
/usr/bin/perperl
/usr/bin/php
/usr/bin/python
/usr/bin/python2.5
/usr/bin/ruby
/usr/bin/tclsh
/usr/bin/tr
/usr/bin/wish
/usr/i586-linux-uclibc/sbin/ldconfig
/usr/lib/util-vserver
/usr/lib/util-vserver/sigexec
/usr/sbin/arping
/usr/sbin/glibc-post-wrapper
/usr/sbin/groupadd
/usr/sbin/groupdel
/usr/sbin/magicfilter
/usr/sbin/update-alternatives
/usr/sbin/update-ldetect-lst
/usr/sbin/update-localtime
/usr/sbin/useradd
/usr/sbin/userdel
/usr/share/haskell-src-exts/register.sh
/usr/share/haskell-src-exts/unregister.sh
/usr/share/hs-plugins/register.sh
/usr/share/hs-plugins/unregister.sh
EOF
   fi
fi

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
%{_sysconfdir}/bash_completion.d/%{name}
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
%dir %{compat_perl_vendorlib}/urpm
%{compat_perl_vendorlib}/urpm.pm
%{compat_perl_vendorlib}/urpm/args.pm
%{compat_perl_vendorlib}/urpm/bug_report.pm
%{compat_perl_vendorlib}/urpm/cfg.pm
%{compat_perl_vendorlib}/urpm/cdrom.pm
%{compat_perl_vendorlib}/urpm/download.pm
%{compat_perl_vendorlib}/urpm/get_pkgs.pm
%{compat_perl_vendorlib}/urpm/install.pm
%{compat_perl_vendorlib}/urpm/lock.pm
%{compat_perl_vendorlib}/urpm/main_loop.pm
%{compat_perl_vendorlib}/urpm/md5sum.pm
%{compat_perl_vendorlib}/urpm/media.pm
%{compat_perl_vendorlib}/urpm/mirrors.pm
%{compat_perl_vendorlib}/urpm/msg.pm
%{compat_perl_vendorlib}/urpm/parallel.pm
%{compat_perl_vendorlib}/urpm/prompt.pm
%{compat_perl_vendorlib}/urpm/removable.pm
%{compat_perl_vendorlib}/urpm/select.pm
%{compat_perl_vendorlib}/urpm/signature.pm
%{compat_perl_vendorlib}/urpm/sys.pm
%{compat_perl_vendorlib}/urpm/util.pm
%{compat_perl_vendorlib}/urpm/xml_info.pm
%{compat_perl_vendorlib}/urpm/xml_info_pkg.pm
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
%ghost %config(noreplace) %_sys_macros_dir/urpmi.recover.macros


