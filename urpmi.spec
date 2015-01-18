%bcond_without	gurpmi
%bcond_without	po
%bcond_without	urpm-tools

Name:		urpmi
Version:	8.03.2
Release:	10
Summary:	Command-line software installation tools
Group:		System/Configuration/Packaging
License:	GPLv2+
Source0:	%{name}-%{version}.tar.xz
Patch1:		urpmi.urpme-lock.patch
Patch2:		urpmi-8.03.2-update-package-priority-list.patch
URL:		https://abf.io/software/urpmi
Requires:	webfetch
Requires:	eject
Requires:	gnupg
Requires:	genhdlist2
Requires:	perl(Time::ZoneInfo)
Requires:	perl(Filesys::Df)
Requires:	perl-File-Sync >= 0.110.0-6
Requires:	meta-task
Requires:	perl-Locale-gettext >= 1.50.0-23
Requires:	perl-Term-ReadKey >= 2.320.0-5
Requires:	perl-XML-LibXML >= 2.11.700-2
Requires:	perl(DateTime)
Requires:	perl(DateTime::Locale)
Requires(post):	gzip
Requires(post):	perl-Locale-gettext
Requires(post):	perl-URPM >= 4.63-1
Suggests:	aria2
BuildRequires:	gettext
BuildRequires:	intltool
BuildRequires:	perl
BuildRequires:	perl-devel
BuildRequires:	perl(File::Slurp)
BuildRequires:	perl(Net::LDAP)
BuildRequires:	perl(URPM)
BuildRequires:	perl(MDV::Packdrakeng)
BuildRequires:	perl(MDV::Distribconf)
BuildRequires:	perl(MDV::Distribconf::Build)
BuildRequires:	perl(Locale::gettext)
%if %{with po}
# fedya
# perl_checker depends from ocaml
# but ocaml not ready for arm64
# and %ifarch macros not available
# for noarch packages
BuildRequires:	perl_checker
%endif
BuildRequires:	intltool
# for make test:
BuildRequires:	perl(Test::Pod)
BuildRequires:	perl(Test::Pod::Coverage)
BuildRequires:	perl(XML::LibXML)
BuildRequires:	glibc-static-devel
BuildRequires:	perl(Net::Server)
# for genhdlist in make test:
BuildRequires:	rpmtools
BuildRequires:	perl(Expect)
BuildArch:		noarch
# temporary deps due to the perl-5.14 bump
#BuildRequires:	perl(IO::Tty)
#BuildRequires:	perl(RPMBDB)
# For urpmi.recover
%if %{with urpm-tools}
Requires:	urpm-tools
%endif
Requires:	perl(Date::Manip)
#ditch for now..
#Requires:	faketime

%description
urpmi is a console-based software installation tool. You can
use it to install software from the console in the same way as you use the
graphical Install Software tool (rpmdrake) to install software from the
desktop. urpmi will follow package dependencies -- in other words, it will
install all the other software required by the software you ask it to
install -- and it's capable of obtaining packages from a variety of media,
including the distribution installation DVD, your local hard disk,
and remote sources such as web or FTP sites.

%if %{with gurpmi}
%package -n	gurpmi
Summary:	User mode rpm GUI install
Requires:	urpmi >= %{EVRD}
Requires:	usermode
Requires:	usermode-consoleonly
Obsoletes:	grpmi < %{version}
Provides:	grpmi = %{version}
Requires(post):	desktop-file-utils
Requires(postun):	desktop-file-utils

%description -n	gurpmi
gurpmi is a graphical front-end to urpmi.
%endif

%package parallel-ka-run
Summary:	Parallel extensions to urpmi using ka-run
Requires:	urpmi >= %{EVRD}
Requires:	parallel-tools

%description parallel-ka-run
urpmi-parallel-ka-run is an extension module to urpmi for handling
distributed installation using ka-run or Taktuk tools.

%package parallel-ssh
Summary:	Parallel extensions to urpmi using ssh and scp
Requires:	urpmi >= %{EVRD} openssh-clients perl

%description parallel-ssh
urpmi-parallel-ssh is an extension module to urpmi for handling
distributed installation using ssh and scp tools.

%package ldap
Summary:	Extension to urpmi to specify media configuration via LDAP
Requires:	urpmi >= %{EVRD}
Requires:	openldap-clients

%description ldap
urpmi-ldap is an extension module to urpmi to allow to specify
urpmi configuration (notably media) in an LDAP directory.

%package dudf
Summary:	Extension to urpmi to handle dudf generation and upload
Requires:	urpmi >= %{EVRD}
Requires:	perl-dudfrpmstatus
BuildRequires:	perl-dudfrpmstatus
BuildRequires:	perl(XML::Writer)
BuildRequires:	perl(Data::UUID)
BuildRequires:	perl(IO::Compress::Gzip)

%description dudf
urpmi-dudf is an extension module to urpmi to allow urpmi to generate
and upload dudf error files. This is a part of the Europeen Mancoosi project,
a project to enhance Linux Package Management. 
See http://www.mancoosi.org/ .

%prep
%setup -q

# unable to reproduce! (#63930)
# urpmi.urpme-lock.patch
#patch1 -p0

%patch2 -p1

%build
perl Makefile.PL INSTALLDIRS=vendor \
%if %{with gurpmi}
    --install-gui \
%endif
%if %{with po}
    --install-po
%endif

%make

# %check
# exit 0
# make test

%install
%makeinstall_std

# bash completion
install -m644 %{name}.bash-completion -D %{buildroot}%{_sysconfdir}/bash_completion.d/%{name}

# for ABF compatibility
ln -s %{_libexecdir}/urpmi.update %{buildroot}%{_sbindir}/urpmi.update
# rpm-find-leaves is invoked by this name in rpmdrake
ln -sf rpm-find-leaves %{buildroot}%{_bindir}/urpmi_rpm-find-leaves

# Don't install READMEs twice
rm -f %{buildroot}%{perl_vendorlib}/urpm/README*

# Desktop entry (only used to register new MIME type handler, so no icon etc.)
%if %{with gurpmi}
install -m644 gurpmi.desktop -D %{buildroot}%{_datadir}/applications/mandriva-gurpmi.desktop
mkdir -p %{buildroot}%{_datadir}/mime/packages
cat > %{buildroot}%{_datadir}/mime/packages/gurpmi.xml << EOF
<?xml version="1.0"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
  <mime-type type="application/x-urpmi">
    <comment>urpmi file</comment>
    <glob pattern="*.urpmi"/>
  </mime-type>
</mime-info>
EOF
%endif

%if %{with po}
%find_lang %{name}
%endif

%preun
if [ "$1" = "0" ]; then
  cd /var/lib/urpmi
  rm -f compss provides depslist* descriptions.* *.cache hdlist.* synthesis.hdlist.* list.*
  cd /var/cache/urpmi
  rm -rf partial/* headers/* rpms/*
fi
exit 0

%if %{with po}
%files -f %{name}.lang
%else
%files
%endif
%doc NEWS README.zeroconf urpmi-repository-http.service
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
# compat symlink for ABF
%{_sbindir}/urpmi.update
%{_libexecdir}/urpmi.update
%{_sbindir}/urpmi.recover
%{_mandir}/man3/gurpm*
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
%{_mandir}/man8/urpmi.recover*
%{_mandir}/man8/urpmi.update*
%{_mandir}/man8/urpmihowto*
%dir %{perl_vendorlib}/urpm
%{perl_vendorlib}/urpm.pm
%{perl_vendorlib}/urpm/args.pm
%{perl_vendorlib}/urpm/bug_report.pm
%{perl_vendorlib}/urpm/cfg.pm
%{perl_vendorlib}/urpm/cdrom.pm
%{perl_vendorlib}/urpm/download.pm
%{perl_vendorlib}/urpm/get_pkgs.pm
%{perl_vendorlib}/urpm/install.pm
%{perl_vendorlib}/urpm/lock.pm
%{perl_vendorlib}/urpm/main_loop.pm
%{perl_vendorlib}/urpm/md5sum.pm
%{perl_vendorlib}/urpm/media.pm
%{perl_vendorlib}/urpm/mirrors.pm
%{perl_vendorlib}/urpm/msg.pm
%{perl_vendorlib}/urpm/orphans.pm
%{perl_vendorlib}/urpm/parallel.pm
%{perl_vendorlib}/urpm/prompt.pm
%{perl_vendorlib}/urpm/removable.pm
%{perl_vendorlib}/urpm/select.pm
%{perl_vendorlib}/urpm/signature.pm
%{perl_vendorlib}/urpm/sys.pm
%{perl_vendorlib}/urpm/util.pm
%{perl_vendorlib}/urpm/xml_info.pm
%{perl_vendorlib}/urpm/xml_info_pkg.pm

%if %{with gurpmi}
%files -n gurpmi
%{_bindir}/gurpmi
%{_libexecdir}/gurpmi2
%{_datadir}/applications/mandriva-gurpmi.desktop
%{_datadir}/mime/packages/gurpmi.xml
%{perl_vendorlib}/gurpmi.pm
%{perl_vendorlib}/gurpm/RPMProgressDialog.pm
%endif

%files parallel-ka-run
%doc urpm/README.ka-run
%dir %{perl_vendorlib}/urpm
%{perl_vendorlib}/urpm/parallel_ka_run.pm

%files parallel-ssh
%doc urpm/README.ssh
%dir %{perl_vendorlib}/urpm
%{perl_vendorlib}/urpm/parallel_ssh.pm

%files ldap
%doc urpmi.schema
%{perl_vendorlib}/urpm/ldap.pm

%files dudf
%doc urpm/README.dudf
%{perl_vendorlib}/urpm/dudf.pm
%{_mandir}/man8/urpmi-dudf.8*
