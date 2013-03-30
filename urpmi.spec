%bcond_without gurpmi

Name:		urpmi
Version:	7.24
Release:	1
Summary:	Command-line software installation tools
Group:		System/Configuration/Packaging
License:	GPLv2+
Source0:	%{name}-%{version}.tar.xz
Patch1:		urpmi.urpme-lock.patch
URL:		https://abf.rosalinux.ru/moondrake/urpmi
Requires:	webfetch
Requires:	eject
Requires:	gnupg
Requires:	genhdlist2
Requires:	perl(Time::ZoneInfo)
Requires:	perl(Filesys::Df)
Requires:	meta-task
# even if this package is still named perl-Hal-Cdroms, it's been updated since
# to use udisks, so please do *NOT* remove...
Suggests:	perl(Hal::Cdroms)
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
BuildRequires:	perl_checker
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
BuildRequires:	perl(IO::Tty)
BuildRequires:	perl(RPMBDB)

%description
urpmi is %{distribution}'s console-based software installation tool. You can
use it to install software from the console in the same way as you use the
graphical Install Software tool (rpmdrake) to install software from the
desktop. urpmi will follow package dependencies -- in other words, it will
install all the other software required by the software you ask it to
install -- and it's capable of obtaining packages from a variety of media,
including the %{distribution} installation DVD, your local hard disk,
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

%build
perl Makefile.PL INSTALLDIRS=vendor \
%if %{with gurpmi}
    --install-gui \
%endif
    --install-po

%make

%check
exit 0
make test

%install
%makeinstall_std

# bash completion
install -m644 %{name}.bash-completion -D %{buildroot}%{_sysconfdir}/bash_completion.d/%{name}

# rpm-find-leaves is invoked by this name in rpmdrake
ln -sf rpm-find-leaves %{buildroot}%{_bindir}/urpmi_rpm-find-leaves

# Don't install READMEs twice
rm -f %{buildroot}%{perl_vendorlib}/urpm/README*

# Desktop entry (only used to register new MIME type handler, so no icon etc.)
%if %{with gurpmi}
install -m644 gurpmi.desktop -D %{buildroot}%{_datadir}/applications/mandriva-gurpmi.desktop
install -m644 gurpmi.xml -D %{buildroot}%{_datadir}/mime/packages/gurpmi.xml
%endif

%find_lang %{name}

%preun
if [ "$1" = "0" ]; then
  cd /var/lib/urpmi
  rm -f compss provides depslist* descriptions.* *.cache hdlist.* synthesis.hdlist.* list.*
  cd /var/cache/urpmi
  rm -rf partial/* headers/* rpms/*
fi
exit 0

%files -f %{name}.lang
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
%{_sbindir}/urpmi.update
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
%{_bindir}/gurpmi2
%{_sbindir}/gurpmi2
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

%changelog
* Sun Aug 5 2012 akdengi <akdengi> 6.70-2
- sync with Cooker

* Fri Jun 29 2012 Arkady L. Shane <arkady.shane@rosalab.ru> 6.69-5
- enable contrib, non-free and restricted for gnome

* Tue Apr 24 2012 akdengi <akdengi> 6.69-3
- /urpm/media.pm If in /etc/product.id version EE enable non-free and restrected by default

* Tue Aug 23 2011 Franck Bui <franck.bui@mandriva.com> 6.68-5mdv2011.0
+ Revision: 696298
- Add a default rule to inst.list for dealing with kernels > 2.6.38

  + Sergey Tuchkin <stuchkin@mandriva.org>
    - sync with cooker
    - urpmi updated to version 6.68
    - urpme bugfix: deadlock in rpm5 /urpmi
      bug: https://qa.mandriva.com/show_bug.cgi?id=63930

  + Alexander Barakin <abarakin@mandriva.org>
    - sync with cooker
    - use rsync to download from rsync-mirrors
      bug: https://qa.mandriva.com/show_bug.cgi?id=53409

* Thu Jun 23 2011 Per Ã˜yvind Karlsen <peroyvind@mandriva.org> 6.66-1
+ Revision: 686791
- new version:
  	o fix disttag/distepoch workaround in previous version resulting in
  	  bogus problem messages

* Wed Jun 01 2011 Per Ã˜yvind Karlsen <peroyvind@mandriva.org> 6.65-2
+ Revision: 682237
- update versioned dependency on perl-URPM to avoid possible breakage (thx to
  Nicolas Pomar?\195?\168de <npomarede@corp.free.fr> for noticing! :)

* Tue May 31 2011 Per Ã˜yvind Karlsen <peroyvind@mandriva.org> 6.65-1
+ Revision: 682090
- new version:
  	o fix orphaning of obsolete packages
  	o fix orphaned packages not being printed when depending packages has
  	  been removed
  	o fix an attempt to create and run an empty transaction
  	o rename --nitronothing to --fastunsafe (more intuitive and less
  	  cheezy;)
  	o fix bug in urpmf, which makes it believe epoch can be found in all
  	  metadata
  	o revert workaround in previous version and implement proper support
  	  for parsing using updated metadata format

* Sat May 28 2011 Per Ã˜yvind Karlsen <peroyvind@mandriva.org> 6.64-1
+ Revision: 681315
- work around issue with *.xml.lzma metadata by fetching some of the data from
  synthesis for now (a bit slower, will do better soon)

* Tue May 24 2011 Per Ã˜yvind Karlsen <peroyvind@mandriva.org> 6.63-1
+ Revision: 678089
- new version:
  	o make 'urpmq --not-available' print fullname
- santize symlink creation of urpmi_rpm-find-leaves

  + Funda Wang <fwang@mandriva.org>
    - there is no mimelnk now

* Mon May 09 2011 Per Ã˜yvind Karlsen <peroyvind@mandriva.org> 6.62-1
+ Revision: 672980
- new version
  	o try tune and improve aria2 parameters for more reliable and faster downloads
  	o reenable aria2 + metalink for downloading metadata by default to make it more reliable

* Fri May 06 2011 Per Ã˜yvind Karlsen <peroyvind@mandriva.org> 6.61-1
+ Revision: 669767
- fix buildrequires for check suite
- new version:
  	o follow some URPM api changes to use proper tag names for requirename & providename

* Wed May 04 2011 Per Ã˜yvind Karlsen <peroyvind@mandriva.org> 6.60-1
+ Revision: 665162
- update translations

* Tue Apr 26 2011 Per Ã˜yvind Karlsen <peroyvind@mandriva.org> 6.59-1
+ Revision: 659489
- add support for --nofdigests & --notriggers
- add README.dudf to %%doc for urpmi-dudf
- move urpmi-dudf.8 man page to urpmi-dudf package
- add buildrequires on perl-dudfrpmstatus
- add dependency on perl-dudfrpmstatus for urpmi-dudf
- new version:
  	o merge DUDF changes from Alexandre Lissy
  	o revert archscore() hack as it's now fixed properly

* Fri Apr 22 2011 Antoine Ginies <aginies@mandriva.com> 6.58-2
+ Revision: 656706
- restore archscore (works now in drakx, installation process)

* Thu Apr 21 2011 Antoine Ginies <aginies@mandriva.com> 6.58-1
+ Revision: 656456
- add missing urpmi-dudf man page
- don't run rpmdb conversion in case of any failures (Per ?\195?\152yvind Karlsen)
- remove archscore(), waiting for platformscrore implementation (Antoine Ginies)

* Thu Apr 21 2011 Antoine Ginies <aginies@mandriva.com> 6.57-2
+ Revision: 656436
- bump release

* Sun Apr 10 2011 Per Ã˜yvind Karlsen <peroyvind@mandriva.org> 6.57-1
+ Revision: 652330
- new version:
  	o drop rpm locking from urpme now that it's safe
  	o drop clean_rpmdb_shared_regions() hacks which seems responsible for
  	  rpmdb locking & corruption issues
  	o allow querying dependencies in urpmf --qf (Pascal Terjan)

* Wed Mar 30 2011 Per Ã˜yvind Karlsen <peroyvind@mandriva.org> 6.56-1
+ Revision: 649194
- drop %%clean section
- new version:
  	o explicitly close transaction and rpmdb after completion
  	o drop '-' in middle of option name from --*debug to really be consistent

* Tue Mar 29 2011 Per Ã˜yvind Karlsen <peroyvind@mandriva.org> 6.55-1
+ Revision: 648757
- new version:
  	o add various --rpm*-debug options corresponding to what rpm provides

* Tue Mar 22 2011 Per Ã˜yvind Karlsen <peroyvind@mandriva.org> 6.54-1
+ Revision: 647704
- don't display README.* files with --test

* Thu Mar 17 2011 Per Ã˜yvind Karlsen <peroyvind@mandriva.org> 6.53-1
+ Revision: 645732
- fix string comparision bug causing urpmi to exit right away if urpmi-dudf
  package isn't installed

* Wed Mar 16 2011 Per Ã˜yvind Karlsen <peroyvind@mandriva.org> 6.52-1
+ Revision: 645690
- cleanups
- drop ancient conflicts and versioned dependencies
- drop compatibility macros not worth maintaining
- drop ancient trigger on urpmi < 4.10.19
- drop trigger on urpmi = 6.0
- drop %%mkrel macro usage
- drop ancient scriptlets
- new release: 6.52
        o only enable legacy compatibility when all packages providing
          mandriva-release in available medias has older version than 2011.0
        o don't exit on errors with DUDF unless user tells to
        o don't modify /var/lib/rpm/installed-through-deps.list when using
          --test

* Sun Feb 27 2011 Funda Wang <fwang@mandriva.org> 6.51-2
+ Revision: 640202
- rebuild to obsolete old packages

* Tue Feb 22 2011 Per Ã˜yvind Karlsen <peroyvind@mandriva.org> 6.51-1
+ Revision: 639309
- new release:
  	o adjust formatting to better fit 80 character column width (#62572)
  	o always print "Installation failed" messages when installing packages
  	  using several transactions and not only when using one transaction

* Sat Feb 19 2011 Per Ã˜yvind Karlsen <peroyvind@mandriva.org> 6.50-1
+ Revision: 638709
- new release:
  	o fix broken 'urpmi --no-md5sum' (#62557)

* Mon Feb 14 2011 Per Ã˜yvind Karlsen <peroyvind@mandriva.org> 6.49-1
+ Revision: 637658
- new release:
  	o require exclusive rpmdb lock for urpme to prevent concurrent rpmdb
  	  access with urpmi
- new release:
  	o print suggests column
  	o increase width of release colum

* Wed Jan 26 2011 Per Ã˜yvind Karlsen <peroyvind@mandriva.org> 6.47-1
+ Revision: 633009
- revert check for rpm in rpmdb before migrating which caused regression

* Tue Jan 25 2011 Per Ã˜yvind Karlsen <peroyvind@mandriva.org> 6.46-1
+ Revision: 632500
- fix urpmq regression introduced in 6.44

* Tue Jan 25 2011 Per Ã˜yvind Karlsen <peroyvind@mandriva.org> 6.45-1
+ Revision: 632498
- new release:
  	o verify that rpm actually was *really* installed before migrating
  	  rpmdb
  	o allow to run 'urpmi --test' as non-root user
- new release:
  	o use URPM::Package->fullname to return pkg as string for urpmq to
  	  get full NVRA
- change versioned perl-URPM dependency to perl-URPM >= 4.8
- new release:
  	o fix db conversion of chroot being run error return value
  	o don't perform rpmdb conversion for chroot when --test is used
- new release: 6.42
  	o fix regression in previous release causing urpmi to try install
  	  rather than upgrading package updates
- new release: 6.41

* Sun Jan 09 2011 Per Ã˜yvind Karlsen <peroyvind@mandriva.org> 6.40-1mdv2011.0
+ Revision: 630719
- new release: 6.40
  	o add support for showing disttag & distepoch

* Mon Nov 22 2010 Eugeni Dodonov <eugeni@mandriva.com> 6.39-1mdv2011.0
+ Revision: 599597
- 6.39:
- install zeroconf documentation and example files.
- resurrect urpmi.recover

* Sat Nov 06 2010 Funda Wang <fwang@mandriva.org> 6.38-2mdv2011.0
+ Revision: 593833
- rebuild for new perl

* Tue Jun 22 2010 Olivier Blin <blino@mandriva.org> 6.38-1mdv2011.0
+ Revision: 548527
- 6.38
- add --zeroconf support in urpmi.addmedia

* Fri May 28 2010 Eugeni Dodonov <eugeni@mandriva.com> 6.37-1mdv2010.1
+ Revision: 546536
- 6.37:
- urpmq
  o fix listing of groups when listing all packages (also fixes #59321)

* Wed May 26 2010 Christophe Fergeau <cfergeau@mandriva.com> 6.36-1mdv2010.1
+ Revision: 546197
- 6.36
- urpmq
  o allow to use -g with --list

* Wed Apr 28 2010 Christophe Fergeau <cfergeau@mandriva.com> 6.35-1mdv2010.1
+ Revision: 540242
- 6.35:
- urpmi.addmedia:
  o disable non-free repository by default for Free edition (#40033)
-urpmi:
  o when using --update, allow package dependencies to be fetched from
    non-update media (#51268)
  o don't confuse media/media keys when a package is available from different
    media (eg CDROM/network)

* Mon Jan 25 2010 Thierry Vignaud <tv@mandriva.org> 6.34-1mdv2010.1
+ Revision: 496473
- don't crash when parsing an invalid media.cfg file in
  /etc/urpmi/mediacfg.d
- fix being unable to run a second transaction set in rpmdrake (#54842)

* Tue Jan 12 2010 Christophe Fergeau <cfergeau@mandriva.com> 6.33-1mdv2010.1
+ Revision: 490280
- 6.33:
- invalidate mirror list cache when it's an old format (ie one which does not
  store the time of product.id)
- fix urpmq --sources documentation (in --help)
- do not advise to reboot when inside a chroot
- do not cache media.cfg from the media when using a virtual one (ie a
  medium for which we don't want to cache metadata)
- ignore gpg_pubkey packages in urpmq --not-available
- fix not being able to remove orphan kernels due to dkms packages (#53414)
- allow use of $RELEASE/$ARCH with urpmi.addmedia --distrib
- fix media redirection (was broken when trying to fix #52276)
- fix bash completion script (#54946)

* Thu Oct 29 2009 Christophe Fergeau <cfergeau@mandriva.com> 6.32-1mdv2010.0
+ Revision: 460165
- 6.23:
- if package B obsoletes package A and if A is in potential orphans and B is
  already installed, don't unconditionally mark B as a potential orphan,
  fixes #54590
- make aria2 disabling work in all cases, should fix #53434 for good.

* Wed Oct 21 2009 Christophe Fergeau <cfergeau@mandriva.com> 6.31-1mdv2010.0
+ Revision: 458580
- 6.31:
- don't use aria2 when loading mirrorlist from api.mandriva.com, fixes #53434
- add --not-available option to urpmq to get a list of packages that are
  installed but not available from any configured media (Pascal Terjan,
  fixes #51418)

* Mon Oct 19 2009 Christophe Fergeau <cfergeau@mandriva.com> 6.30.1-1mdv2010.0
+ Revision: 458235
- 6.30.1:
- add --download-all option to gurpmi too
- add missing Requires on Perl::Filesys::Df
- add missing Requires for the new --download-all option

* Fri Oct 16 2009 Christophe Fergeau <cfergeau@mandriva.com> 6.30-1mdv2010.0
+ Revision: 457923
- 6.30:
- unbreak kernel orphans management (broken by #53425 fix)
- improve messages asking to restart system/session (#53126)
- add --download-all option to download all packages before attempting
  to start installation
- fix priviledge escalation in rurpmi and rurpme (#54568)
- when the database is locked, print the PID of the processus locking it
 (#38923, Pascal Terjan)

* Mon Oct 05 2009 Christophe Fergeau <cfergeau@mandriva.com> 6.29-1mdv2010.0
+ Revision: 454171
- 6.29:
- downgrade skipped package log message to debug message
- make sure we don't check certificate in aria2 except when we want to
- exclude kernel-source from orphan processing (#53426)
- do not list as orphans kernel packages which where not installed through
  dependencies (#53425)

* Tue Sep 15 2009 Christophe Fergeau <cfergeau@mandriva.com> 6.28.2-1mdv2010.0
+ Revision: 443039
- 6.28.2:
- exclude kernel-source from orphan processing (#53426)
- translation updates

* Thu Sep 03 2009 Christophe Fergeau <cfergeau@mandriva.com> 6.28.1-1mdv2010.0
+ Revision: 428280
- 6.28.1:
  o make sure we don't create empty /url files

* Mon Aug 31 2009 Christophe Fergeau <cfergeau@mandriva.com> 6.28-1mdv2010.0
+ Revision: 422987
- urpmi 6.28:
- urpmi.addmedia:
  o use https when downloading the mirror list from api.mandriva.com, and
- orphans handling
  o do not offer to remove current kernel (even if it's not a official
    kernel
  o offer to remove old kernels (excluding the running one)
    (also do not do anything regarding kernels if we failed to detect
    the running one (ie: chroot))

* Tue Aug 18 2009 Christophe Fergeau <cfergeau@mandriva.com> 6.27.1-1mdv2010.0
+ Revision: 417769
- 6.27.1:
- make sure error messages are displayed (was broken as part of fix #50776)
- don't attempt to expand empty URLs, fixes bug #52860
- append a reason to api.mandriva.com queries when we are doing it because
  the cache is outdated

* Thu Aug 13 2009 Thierry Vignaud <tv@mandriva.org> 6.27-1mdv2010.0
+ Revision: 416072
- prevent garbaging text installer screen (#50776)
- urpmq:
  o -a option was ignored when using --src (fixes #52672)
- urpmi.addmedia:
  o properly expand $RELEASE, $ARCH and $HOST in media URLs (fixes #52276)
  o add support for /etc/urpmi/mediacfg.d which stores the media.cfg files
    for the media entries in urpmi.cfg

* Fri Jul 31 2009 Christophe Fergeau <cfergeau@mandriva.com> 6.26.1-1mdv2010.0
+ Revision: 405202
- perl modules are BuildRequires since they are used in make test
- 6.26.1:
- dudf fixes
- 6.26:
- urpmi.addmedia:
  o properly invalidate mirror cache when the distro version changes
    (ie when product.id changes). Fixes bug #52133, patch from
    Aur?\195?\169lien Lefebvre
- urpmi:
  o allow bash-completion to complete to .spec files as well
  o adjust parsing of aria2 output for aria2 1.4, fixes bug #51354
    (patch from Funda Wang)
  o use urpmi log API for the transaction failed message instead of
    printing it on the console so that installer can save each error
    with each transaction log instead of only having a summary at end
  o inform user when selected packages conflict instead of silently
    dropping one (Anssi Hannula)
  o add optionnal dudf module to send dudf data to the mancoosi
    research project (Olivier Rosello)

* Thu Apr 23 2009 Thierry Vignaud <tv@mandriva.org> 6.25.5-1mdv2009.1
+ Revision: 368812
- gurpmi:
  o do not advise to restart in --auto mode
  o log bad signatures on stderr

* Mon Apr 20 2009 Christophe Fergeau <cfergeau@mandriva.com> 6.25.4-1mdv2009.1
+ Revision: 368413
- 6.25.4:
- add NoDisplay=true to gurpmi.desktop

* Sat Apr 18 2009 Pascal Terjan <pterjan@mandriva.org> 6.25.3-1mdv2009.1
+ Revision: 367962
- fix gurpmi.desktop (#50047)

* Wed Apr 15 2009 Thierry Vignaud <tv@mandriva.org> 6.25.2-1mdv2009.1
+ Revision: 367577
- translation updates
- move .desktop entry from inlined in spec into a real file (requested by translators)

* Tue Mar 31 2009 Thierry Vignaud <tv@mandriva.org> 6.25.1-1mdv2009.1
+ Revision: 363049
- prevent rpmdrake from crashing (#49354), side effect of #49226 fix

* Tue Mar 31 2009 Thierry Vignaud <tv@mandriva.org> 6.25-1mdv2009.1
+ Revision: 362970
- downgrade cryptic log message to debug message, fixes #49226
- enable installer to cancel installation

* Fri Mar 27 2009 Christophe Fergeau <cfergeau@mandriva.com> 6.24-1mdv2009.1
+ Revision: 361612
- 6.24:
- return error code when user aborts gurpmi/gurpmi2

* Wed Mar 25 2009 Christophe Fergeau <cfergeau@mandriva.com> 6.23-1mdv2009.1
+ Revision: 361071
- 6.23:
- log user interactions to stdout in gurpmi2
- exit with non 0 error code when failing to add a media, fixes bug #47952
- when using urpme -a, properly report when no packages could be removed,
  fixes bug #48506
- return a non 0 error code when the user stops the install when an upgrade
  would remove some packages (because of dependencies issues)
- fix a circular reference that was causing rpmdb to be opened many
  times in installer

* Mon Mar 09 2009 Thierry Vignaud <tv@mandriva.org> 6.22.4-1mdv2009.1
+ Revision: 353275
- change installer API (in order to fix detecting whether installing ackages
  succedded or not)
- bump require on perl-URPM

* Thu Mar 05 2009 Thierry Vignaud <tv@mandriva.org> 6.22.3-1mdv2009.1
+ Revision: 348830
- urpmi
  o fix verifying packages signatures in chrooted environments (especially
    important for installer where there's no rpmdb in / (really /var/lib/rpm)
    and thus no keys to check against)

* Wed Mar 04 2009 Thierry Vignaud <tv@mandriva.org> 6.22.2-1mdv2009.1
+ Revision: 348335
- close another fd leak (needed for drakx)

* Wed Mar 04 2009 Thierry Vignaud <tv@mandriva.org> 6.22.1-1mdv2009.1
+ Revision: 348277
- explicitely close the RPM DB on comleting transaction (needed for drakx)

* Tue Mar 03 2009 Thierry Vignaud <tv@mandriva.org> 6.22-1mdv2009.1
+ Revision: 347985
- drop support for /etc/urpmi/media.d/*.cfg
  (was partially broken, non documented and hopefully unused)
- add more callbacks for installer
- fix reading descriptions with --env=
- only load LDAP binding if needed (saves a couple MB in rpmdrake)
- gurpmi:
  o warn when rebooting is needed after installing packages

* Tue Jan 13 2009 Christophe Fergeau <cfergeau@mandriva.com> 6.21-1mdv2009.1
+ Revision: 329028
- 6.21:
- drop urpmi.recover
  (no more possible with rpm 4.6 which doesn't handle --repackage)
- Version 6.20 - 13 January 2009
- urpmi
  o --auto: do not prompt for "retry" on aria2 download failure
    (regression introduced in 6.18)
  o add aria2 to the priority list of packages that need to be updated
    before restarting urpmi
  o fix issue with urpmi sometimes using the wrong key when checking
    signatures when the same package is available from different media
  o remove packages from installed-through-deps.list when they are explicitly
    requested using urpmi (even if they were already installed) (#45054)
- urpmi_rpm-find-leaves
  o do not list suggested packages as unrequested packages (#46326)
- urpmq
  o fix urpmq -i on local RPMs

  + Pixel <pixel@mandriva.com>
    - do not package urpmi.recover anymore since it doesn't work with rpm 4.6.0
      (which dropped support for --repackage)

* Mon Nov 24 2008 Pixel <pixel@mandriva.com> 6.19-1mdv2009.1
+ Revision: 306349
- "make test" now need -lc
- 6.19:
- urpmi
  o in --auto, do display an error message when rpms are missing
  o in --auto, do not allow to install a package substring match
    (you can use -a to force it)
  o revert --auto-update behaviour in case of media update failures (#45417)
  o ensure download when updating media (with --auto-update) is quiet
- urpmi.update
  o updated "ignore"d medium should not become non "ignore"d (#45457)
    (regression introduced in 6.18)

* Tue Oct 28 2008 Pixel <pixel@mandriva.com> 6.18-1mdv2009.1
+ Revision: 297965
- cleanup installed-through-deps.list from potentially wrong entries due to
  bug #45058
- urpmi, gurpmi
  o prompt for "retry" on aria2 download failure
  o retry once on aria2 versioned-file download failure
  o allow setting aria2-options in urpmi.cfg
- urpmi
  o fix "urpmi firefox mozilla-firefox-ext-google-toolbar ;
    urpme --auto-orphans mozilla-firefox-ext-google-toolbar" which must not
    remove firefox (cf #45058)
    (this is especially bad for DrakX/rpmsrate)
  o fix --auto-update ignoring --media and default-media (#45097)
- gurpmi
  o display the download errors
  o log all urpmi logs
  o fix answering yes to questions on error
- urpmi.update
  o fix --force-key (#45094)
- urpmi.addmedia
  o do not allow "/" in media name (#44765)
- urpmi.update, urpmi.addmedia
  o exit on failing media instead of ignoring them
    (esp. for urpmi.addmedia --distrib).
    exceptions: "urpmi.update -a" and "urpmi.update --update"
                for backward compatibility

* Tue Oct 14 2008 Pixel <pixel@mandriva.com> 6.17-1mdv2009.1
+ Revision: 293744
- 6.17:
- urpmi
  o diskspace issues are now a fatal error (need perl-URPM 3.20)
    (no use going on with the other transactions)
- gurpmi
  o add support for --clean
- urpmi.update, urpmi.addmedia, urpmi.removemedia:
  o do not check wether the media are valid,
    it allows "mv /etc/urpmi/urpmi.cfg.{backup,} ; urpmi.update -a" to work
    (nb: not equivalent with urpmi.addmedia, since pubkey will not be imported)
- aria2:
  o do not use --max-file-not-found=3 when downloading rpms
    (since rpms are "versioned")
  o use it even if nearest mirror is rsync
- library:
  o allow mdkapplet-upgrade-helper to force $MIRRORLIST distro version

* Wed Oct 08 2008 Pixel <pixel@mandriva.com> 6.16-1mdv2009.0
+ Revision: 291206
- 6.16:
- urpmi:
  o fix displaying "bad signature" in non-utf8 (#44587)
- gurpmi:
  o overall progress-bar, display the download speed, nicer looking
  o [bugfix for 6.15] re-allow to continue on bad signature

* Tue Oct 07 2008 Thierry Vignaud <tv@mandriva.org> 6.15-1mdv2009.0
+ Revision: 291159
- urpmi, rpmdrake:
  o nice exit code for "bad signature" fatal error. Fixes rpmdrake continuing
    on bad signature (#44575)
- urpmi, gurpmi:
  o handle --replacefiles (will be used by mdkonline)
    (require perl-URPM 3.19)
- gurpmi:
  o do not exit in --auto mode at end of installation which prevents
    restarting after priority upgrade
  o fix using --rpm-root & --urpmi-root
  o just do not ask for confirmation before removing packages in
     --auto mode,

* Tue Sep 23 2008 Pixel <pixel@mandriva.com> 6.14-1mdv2009.0
+ Revision: 287390
- 6.14:
- use "versioned" media_info files
  (needed for aria2 to handle mirrors not having some media_info/*)
- urpmi.addmedia, urpmi.update:
  o for remote media, instead of first checking reconfig.urpmi, try MD5SUM.
    If it fails try reconfig.urpmi
  o only look for "descriptions" in media_info/
  o do not get "descriptions" on non update media since it's useless and
    potentially slow
- urpmi.addmedia:
  o --distrib: do not skip "debug_for=" media
    (debug media will be added with flag "ignore" if noauto=1)
  o for remote media, do not probe for media_info files in "./", do it only in
    "media_info/"
- aria2:
  o use --ftp-pasv (as suggested by aria2 developer)
  o use --connect-timeout 6 seconds (instead of 3)

* Fri Sep 19 2008 Pixel <pixel@mandriva.com> 6.13-2mdv2009.0
+ Revision: 285806
- conflict with aria2 version not handling --max-file-not-found

* Thu Sep 18 2008 Pixel <pixel@mandriva.com> 6.13-1mdv2009.0
+ Revision: 285690
- 6.13:
- aria2:
  o use new option --connect-timeout (need aria2 20080918 snapshot)
  o abort download after not finding a file on 3 servers
  o reduce from 16 to 8 servers for each file in metalink

* Wed Sep 17 2008 Thierry Vignaud <tv@mandriva.org> 6.12-1mdv2009.0
+ Revision: 285458
- when using --bug,
  o copy /root/.rpmdrake too
  o copy updates descriptions too

* Thu Sep 11 2008 Pixel <pixel@mandriva.com> 6.11-1mdv2009.0
+ Revision: 283813
- 6.11:
- library:
  o create urpm::select::conflicting_packages_msg() for rpmdrake

* Tue Sep 09 2008 Thierry Vignaud <tv@mandriva.org> 6.10-1mdv2009.0
+ Revision: 283176
- library:
  o enable rpmdrake to support --debug, --env, -q & -v options
  o fix urpm::download::sync() return value (used by rpmdrake) (#43639)

* Tue Sep 09 2008 Pixel <pixel@mandriva.com> 6.9-1mdv2009.0
+ Revision: 283039
- 6.9:
- urpmi
  o after installing in chroot, migrate back rpmdb db version to one
    compatible with the rpm in the chroot
  o fix orphans handling: an already installed pkg must not become
    "unrequested" because a new version of it is required
- fix display of downloaded urls with aria2 and metalinks
- fix handling --downloader when using mirrorlist (it was forcing aria2)

* Thu Sep 04 2008 Pixel <pixel@mandriva.com> 6.8-1mdv2009.0
+ Revision: 280835
- 6.8:
- fix proxy parameter for aria2
- remove rsync mirrors when calling aria2
- urpmi
  o enhance --bug: copy installed-through-deps.list in bug report
- gurpmi, gurpmi2:
  o silence perl warnings (ie remove "use warnings")
- library:
  o modify urpm::download::get_content() to work as non-superuser

* Wed Sep 03 2008 Pixel <pixel@mandriva.com> 6.7-1mdv2009.0
+ Revision: 279658
- 6.7: really call aria2 with --max-tries=1
  (it helps a lot when trying to download some files (eg: reconfig.urpmi))

* Tue Sep 02 2008 Pixel <pixel@mandriva.com> 6.6-1mdv2009.0
+ Revision: 279101
- conflict with aria2 < 0.15.3 (to ensure it handles --uri-selector=adaptive)
- 6.6: call aria2 with brand-new --uri-selector=adaptive

* Mon Sep 01 2008 Pixel <pixel@mandriva.com> 6.5-1mdv2009.0
+ Revision: 278493
- 6.5:
- all tools
  o use metalink/aria2 by default (when available) when using a mirrorlist
- urpmi, urpmq
  o do not display all substring matches on stderr, only a subset of them, and
    suggest to use "-a" to use all matches (#38956)
- urpmi
  o do not write useless "foo (obsoletes foo-xxx)" in
    installed-through-deps.list (#42167)
- urpmi.addmedia
  o instead of discarding --update when using --distrib, give it a meaning:
    only add media flagged "update"
  o handle $URPMI_ADDMEDIA_REASON
    (special reason to give to api.mandriva.com/mirrors/... to allow statistics)
- gurpmi2
  o nicer default window size
  o render nicely under matchbox during install
  o handle --update

  + Nicolas LÃ©cureuil <nlecureuil@mandriva.com>
    - Add missing semicolon on x-urpmi.desktop

* Thu Aug 14 2008 Thierry Vignaud <tv@mandriva.org> 6.4-1mdv2009.0
+ Revision: 271986
- fix build: BuildRequires perl_checker
- gurpmi
  o fix exit code if canceling when requested to select a choice
  o fix exit code if refusing to insert the proper media
  o notify callers when installation is canceled (#40358)
- gurpmi
  o better handle closing dialogs
  o fix not asking questions on error
- gurpmi
  o handle --justdb and --noscripts
  o fix/manage --urpmi-root
- urpme
  o add --justdb
  o sort the list of orphans

* Thu Jul 10 2008 Pixel <pixel@mandriva.com> 6.1-1mdv2009.0
+ Revision: 233523
- 6.1:
- all tools
  o fix broken ssh:// (regression introduced in 6.0)
- urpmi, urpme, urpmq:
  o fix orphans handling: suggested packages must not be detected as orphans
- urpmi:
  o handle README.urpmi in utf8 (but not other encodings) (#41553)
  o handle --debug-librpm
  o fix --parallel on local media (ie when synthesis.cz is not copied to /var/lib/urpmi)
  o fix --parallel --auto-select when one box is up-to-date but not the others (#41924)
  o fix creation of chroot with --root by using /var/lib/rpm/installed-through-deps.list
    (instead of having it in /var/lib/urpmi)
- urpmi.addmedia:
  o make --mirrorlist with no url equivalent to --mirrorlist '$MIRRORLIST' (#40283)
  o --interactive: fix selecting "noauto" media (#39522)
- urpmq:
  o --suggests now displays the suggested packages, see --allow-suggests for
    previous behaviour (#39726)
  o add --obsoletes
- urpme:
  o --test: display "Removal is possible" if no pb (#40584)

* Tue Jul 08 2008 Pixel <pixel@mandriva.com> 6.0-1mdv2009.0
+ Revision: 232697
- 6.0:
- all tools:
  o handle "unrequested orphans" (similar to "deborphan")
  o statedir files are now in /var/lib/urpmi/<medium-name>/
      for eg: /var/lib/urpmi/synthesis.hdlist.<medium-name> is now
      /var/lib/urpmi/<medium-name>/synthesis.hdlist.cz
    it allows easier medium update without using urpmi.update (#31893)
    (but with --urpmi-root, old statedir files are used to allow compatibility
    with older urpmi)
  o fix handling --urpmi-root <relative dir>
- gurpmi:
  o do cancel when pressing the 'No' button (#41648)
- urpmi:
  o "missing file" and "bad rpms" errors are reported asap
    and are fatal errors unless the user wants to go on anyway (or --force)
  o display a message "Package foo is already installed" when asking
    "urpmi foo bar" and only installing bar (#41593)
    (requires perl-URPM 3.18)
  o set connection timeout for rsync as well (Anssi)
  o fix --replacepkgs when a same package appears more than once in urpmi db
  o fix displaying "files are missing" (regression introduced in 5.6)
  o tell bash-completion urpmi handles file names (#41699) (guillomovitch)
- urpmi.addmedia, urpmi.update:
  o fix --no-md5sum (regression introduced in 5.20) (#41237)
- urpme:
  o indent the packages to be removed
  o enhance error message "Removing the following package will break your system"
- rpm filetriggers deprecates update_menus/update_scrollkeeper/update_mime_database/update_icon_cache/update_desktop_database/post_install_gconf_schemas

* Mon Jun 02 2008 Pixel <pixel@mandriva.com> 5.20-1mdv2009.0
+ Revision: 214211
- 5.20:
- urpmi:
  o --auto-update should behave like urpmi.update when mirrorlist is outdated
    (cf http://forum.mandriva.com/viewtopic.php?t=86837)
  o fix --replacepkgs when a package appears more than once in urpmi db (#40893)
    (need perl-URPM 3.14)
- urpmi.addmedia:
  o add missing mark in "Do you want to add media '%%s'?" message (from Nikos)
- urpmi.addmedia, urpmi.update:
  o fix checking synthesis MD5SUM
  o check downloaded synthesis/MD5SUM is not invalid HTML code, and try
    another mirror from mirrorlist (#39918)
    (useful for servers not returning a valid HTTP error)

* Thu Apr 03 2008 Pixel <pixel@mandriva.com> 5.19-2mdv2008.1
+ Revision: 192226
- fix upgrading from Mandriva 2007.1 and 2008.0
  (ie the distros where urpmi has urpm/media.pm and so urpm::media::clean()
  instead of urpm::clean())

* Thu Apr 03 2008 Pixel <pixel@mandriva.com> 5.19-1mdv2008.1
+ Revision: 192185
- 5.19:
- urpmq:
  o --suggests is currently misleading, introduce --allow-suggests and explain
    the user that --suggests really means --allow-suggests (#39726)

* Tue Apr 01 2008 Pixel <pixel@mandriva.com> 5.18-1mdv2008.1
+ Revision: 191378
- 5.18:
- urpmi.addmedia, urpmi.update:
  o correctly handle media with no xml-info when using "xml-info: always"
    (#39521)
- urpmi.addmedia:
  o --mirrorlist: if the retrieved media.cfg is broken, try another mirror
    (#39591, it also workarounds #39592)
- urpmf:
  o check usage of -a, -! and the like instead of displaying the ugly
    "Internal error: syntax error ..."
  o in some cases (iso on disk), the hdlist is not available in
    media/xxx/media_info/, but we can use the statedir copy. So use it

* Fri Mar 28 2008 Pixel <pixel@mandriva.com> 5.17-1mdv2008.1
+ Revision: 190937
- 5.17:
- urpmi:
  o nice error message when hal daemon is not running and is needed (#39327)
- urpmq:
  o do not use rpms on removable cdrom media (#39396)
- urpmf, urpmq:
  o display an error message when /etc/urpmi/proxy.cfg can't be read
- urpmi.update, urpmi.addmedia:
  o do not restrict read on /etc/urpmi/proxy.cfg if it doesn't contain
    passwords (#39434)

* Tue Mar 25 2008 Pixel <pixel@mandriva.com> 5.16-1mdv2008.1
+ Revision: 189906
- 5.16:
- urpmi:
  o fix getting rpms from different media on same DVD
  o handle displaying utf8 download progression in non-utf8 terminal
    (ie clean the full line when we can't be sure of the number of characters
    that will be displayed)
- urpmq:
  o fix --list -r (#39287) (regression introduced in 5.7)
- bash-completion (guillomovitch):
  o don't complete on available packages if completed item is clearly a file
  o only select available packages for selected medias
  o fix rurpmi completion

* Tue Mar 18 2008 Pixel <pixel@mandriva.com> 5.15-1mdv2008.1
+ Revision: 188522
- 5.15:
- urpmi.addmedia, urpmi.update:
  o urpmi.addmedia --mirrorlist handles a list of mirrors/mirrorlist:
    you can specify a mirror to use inside a local network, but it will
    default to standard mirrors when the local mirror is not available.

* Mon Mar 17 2008 Pixel <pixel@mandriva.com> 5.14-1mdv2008.1
+ Revision: 188392
- 5.14:
- urpmi:
  o tell the user to "restart system" when it is needed
  o nicer error message when database is locked (#38923)

* Mon Mar 17 2008 Pixel <pixel@mandriva.com> 5.13-1mdv2008.1
+ Revision: 188257
- fix upgrading from Mandriva 2007.0
  (urpm::update_media() doesn't correctly do a second pass to handle file deps
  (eg: /sbin/fuser))
- 5.13:
- gurpmi:
  o handle provides (spotted by salem)
  o handle -p and -P like urpmi
- urpmi:
  o never suggest --install-src for spec file (#38876)
  o do not allow "urpmi --install-src foo.spec"

* Fri Mar 14 2008 Pixel <pixel@mandriva.com> 5.12-2mdv2008.1
+ Revision: 187875
- handle rebuild of synthesis from hdlist for old urpmi using old urpmi
  (since recent urpmi never build synthesis)

* Thu Mar 13 2008 Thierry Vignaud <tv@mandriva.org> 5.12-1mdv2008.1
+ Revision: 187450
- gurpmi:
  o ensure rpm error message are always in UTF-8
  o ensure urpmi messages are always in UTF-8
  o handle --force
  o return 1 like urpmi if package doesn't exist
  o return urpmi error code
  o translate usage

* Tue Mar 11 2008 Pixel <pixel@mandriva.com> 5.11-1mdv2008.1
+ Revision: 186300
- 5.11:
- gurpmi:
  o fix breakage introduced with priority upgrades support (#38738) (tvignaud)
- bash-completion:
  o restore available-pkgs completion using "urpmq --list" by default
    (it needed COMP_URPMI_HDLISTS to be set, but it should be fast enough now)
- urpmi:
  o have a nicer error message when perl-Hal-Cdroms is missing (#38778)
  o do handle suggests in priority upgrades (#38778)

* Fri Mar 07 2008 Thierry Vignaud <tv@mandriva.org> 5.9-1mdv2008.1
+ Revision: 181416
- modify infrastructure so that rpmdrake doesn't select all updates by
  default (#38611)

* Thu Mar 06 2008 Thierry Vignaud <tv@mandriva.org> 5.8.1-1mdv2008.1
+ Revision: 180963
- add infrastructure so that rpmdrake doesn't select all updates by
  default (#38611)

  + Pixel <pixel@mandriva.com>
    - suggesting perl-Hal-Cdroms which is very useful now for cdrom media (#38510)
    - require genhdlist2 (which is now in its own package) (#38510)

* Wed Mar 05 2008 Thierry Vignaud <tv@mandriva.org> 5.8-1mdv2008.1
+ Revision: 179306
- add infrastructure so that gurpmi & rpmdrake can handle priority
  upgrade list
- add callbacks so that rpmdrake can reuse more urpmi code
- gurpmi:
  o handle priority upgrade list
- urpmi:
  o do not pretend removing packages from cache when there's nothing
    to remove

* Mon Mar 03 2008 Pixel <pixel@mandriva.com> 5.7-1mdv2008.1
+ Revision: 178105
- 5.7:
- all tools:
  o cdrom:// replaces removable://
  o use hal to wait-for/mount cdroms:
    you can now use more than one cdrom drive
  o fix download progression using wget
  o restore generation of /var/lib/urpmi/names.<medium>, but it is now done in
    urpmq/urpmi/urpmf (and so only if used as root)
- gurpmi:
  o exit immediately on success in automatic mode
  o fix --auto-select option
  o fix --root option
  o give the focus to buttons (Emmanuel Blindauer, #38047)
  o handle --allow-medium-change (needed for drakxtools)
  o handle --expect-install (needed for drakxtools)
  o handle --test
  o reuse common shared code of urpmi
- urpmf, urpmq:
  o never display raw downloader output, otherwise output is very messy (#38125)
  o do not try to download xml-info if it's not available (#38125)
- urpmi.addmedia:
  o fix --distrib for cdroms (#30613)
- urpmi:
  o fix --expect-install (broken since 4.9.30!)
  o fix using proxy with curl (#38143)
  o do not copy rpms from cdrom if only one cdrom is used (#28083)
- urpmf:
  o fix searching for more than one pattern (#38286)
- urpmq:
  o --list: speed it up (2.5x faster, and 6x faster with names.<medium>)

* Tue Feb 26 2008 Pixel <pixel@mandriva.com> 5.6-1mdv2008.1
+ Revision: 175201
- 5.6:
- urpmq:
  o add --conflicts
  o --requires now display the raw requires, use --requires-recursive to get
    the old behaviour (#29176)
  o make "urpmq --list xxx" display "use -l to list files" and exit on error
- urpmf:
  o fix mirrorlist handling
  o fix fallback on hdlist when xml-info not found
- urpmi, urpmi.addmedia, urpmi.update:
  o have fatal errors on some errors that must not happen (eg: moving rpm from
    download dir to cachedir)
  o handle variables $ARCH/$RELEASE in mirrorlist
- urpmi:
  o display "%%s of packages will be retrieved."
    (need perl-URPM 3.10 and synthesis built with @filesize@)
  o do not say "files are missing" when the downloaded rpm is corrupted
  o --test: only display "Installation is possible" when it is the case (#29837)
  o fix "using one big transaction" that occurs when using --keep
    (#30198) (part of the fix is in perl-URPM 3.09)
- bash-completion:
  o restore available-pkgs completion using "urpmq --list" (guillomovitch)
    (but only if COMP_URPMI_HDLISTS is set since it's slow)

* Sun Feb 24 2008 Pixel <pixel@mandriva.com> 5.5-1mdv2008.1
+ Revision: 174118
- 5.5:
- all tools:
  o handle mirrorlist
    (need perl-Zone-TimeInfo patched for geolocalisation)
- urpmf
  o fallback on hdlist when xml-info not found (useful for old distribs)
- urpmi handles /etc/urpmi/media.d/*.cfg
  as an alternative to using urpmi.addmedia
- urpmi.update, urpmi.addmedia:
  o handle --virtual for remote media
    (a better name would be "auto-update") (a la yum)
  o do not parse synthesis (relying on MD5SUM for corruption detection)
  o drop /var/lib/urpmi/names.<medium> (was used by bash-completion)
- urpmi.addmedia
  o don't fail on remaining statedir files (#36267)
    (especially useful when using media.d/*.cfg)
- merge conflicting urpmi.recover.macros lines in %%file
- fix URL (urpmi is no more on cpan since rgs removed it)

* Tue Feb 05 2008 Pixel <pixel@mandriva.com> 5.4-1mdv2008.1
+ Revision: 162621
- 5.4, bug fix release:
- urpmi, urpme, urpmq, urpmf:
  o fix --use-distrib

* Mon Feb 04 2008 Pixel <pixel@mandriva.com> 5.3-1mdv2008.1
+ Revision: 162315
- 5.3:
- urpmi.cfg:
  o "media_info_dir: media_info" is the default
  o "no-media-info" is used for media for which media_info must be built from
    rpms
- urpme, urpmi:
  o add basesystem-minimal to prohibit-remove
- urpme:
  o enhance pkg list formatting for "The following packages contain %%s: %%s"
    error message (#29178)
- urpmf:
  o fix --synthesis (it may break urpmq/urpmi --synthesis)
- urpmq:
  o add --no-suggests
- library:
  o since any_xml_info can be slow, add a "callback" option (#37264)

* Fri Jan 18 2008 Pixel <pixel@mandriva.com> 5.2-1mdv2008.1
+ Revision: 154708
- 5.2:
- urpmi:
  o --buildrequires deprecate --src, --src is kept for compatibility but its
    behaviour is changed a little (it doesn't download src.rpm anymore)
  o --install-src as user now works for remote medium
  o --install-src will remove succesfully installed src.rpm from
    /var/cache/urpmi/rpms/* (unless post-clean is 0)
- urpmf:
  o add special code for --files simple case, it makes urpmf 3x faster for
    this often used case
  o display a warning when searching "xxx(yyy)" since it is handled as a
    regexp and so the parentheses are useless. suggest using --literal
- urpmq:
  o add --provides
  o fix option -a : display packages of all compatible archs (#36942)
- all tools:
  o deprecate --curl and --wget in favor of --downloader curl
    and --downloader --wget
  o fix displaying error message when failing to lock (regression in 5.1)

* Wed Jan 16 2008 Pixel <pixel@mandriva.com> 5.1-1mdv2008.1
+ Revision: 153670
- 5.1:
- urpmf, urpmq:
  o fix using xml info files with spaces in medium name
- urpmf:
  o fix --license
- urpmq:
  o add --sourcerpm
  o deprecate "urpmq --requires", "urpmq -R" and "urpmq -RR"
  o fix --list (regression introduced in 5.0) (#36742)

* Fri Jan 11 2008 Pixel <pixel@mandriva.com> 5.0-1mdv2008.1
+ Revision: 148594
- 5.0:
- urpmf, urpmq:
  o use xml info instead of hdlist when possible
    o "urpmq -l" is faster (3x)
    o "urpmf -l" is slower (1.5x)
    o "urpmf --sourcerpm" is much faster
    o see "xml-info" option in urpmi.cfg(5) to see when those files are downloaded
    o new require: perl module XML::LibXML
- urpmq:
  o use rpm file instead of hdlist/xml-info when file is local
  o use URPM::Package->changelogs (need perl-URPM 3.06)
- urpmf
  o fix an *old* bug (since december 2002) making urpmf keeps parsed
    hdlist files in memory (was fixed for multitags, but not for simple tags)
- all tools:
  o replace /var/lib/urpmi/MD5SUM with /var/lib/urpmi/MD5SUM.<medium_name>
    (this will allow checking xml media_info is up-to-date even if we don't
    update it at the same time as synthesis is updated)
- urpmi.update, urpmi.addmedia, urpmi.removemedia:
  o drop hdlist support replaced with xml media_info
    (this imply file-deps are correctly handled, see genhdlist2(1))
  o drop option "-c" which used to clean /var/cache/urpmi/headers
  o enhancement: only parse updated synthesis
- urpmi.addmedia
  o do check md5sum of downloaded synthesis
    (the check was only done on urpmi.update)
  o new --xml-info option
- urpmi:
  o do remove __db* on priority-upgrade
    (fix regression introduced in 4.10.15)
  o always prompt before doing a priority-upgrade transaction, even if there
    is only one priority upgrade package (since there will be more packages to
    install after restarting urpmi)

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

* Fri Dec 21 2007 Pixel <pixel@mandriva.com> 4.10.20-1mdv2008.1
+ Revision: 136184
- 4.10.20:
- urpmi:
  o do remove __db* on priority-upgrade
    (fix regression introduced in 4.10.15)

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Wed Dec 12 2007 Pixel <pixel@mandriva.com> 4.10.19-1mdv2008.1
+ Revision: 117838
- 4.10.19:
- urpmi:
  o fix handling "post-clean: 0" in urpmi.cfg
    (#36082, regression introduced in 4.10.16)
- library:
  o urpm::media::read_config() doesn't read urpmi.cfg global options anymore,
    use urpm->get_global_options or urpm->new_parse_cmdline

* Tue Dec 11 2007 Pixel <pixel@mandriva.com> 4.10.18-1mdv2008.1
+ Revision: 117191
- 4.10.18:
- urpmi:
  o handle --suggests (to override urpmi.cfg global option "no-suggests")
- urpmi.update:
  o exit code 1 when a (selected) medium can't be updated (#35952)
  o leave early with error if no medium were successfull updated
- drop translated man pages (they are too old)
- urpmi.addmedia:
  o exit code 1 when a medium can't be added
  o enhance parsing of urls with login:password for logins with "@"
    so that password doesn't end up in urpmi.cfg
  o adapt to perl-URPM 3.00 API to parse pubkey files
    (nb: $urpm->{keys} is not used anymore)
- require perl(Date::Manip) instead of perl-DateManip
  (ie follow our perl policy)

  + Guillaume Rousse <guillomovitch@mandriva.org>
    - bash completion is not configuration

* Fri Nov 30 2007 Pixel <pixel@mandriva.com> 4.10.17-1mdv2008.1
+ Revision: 114014
- 4.10.17:
- urpmi:
  o fix regression introduced in 4.10.15:
    "urpmi --force valid invalid" should warn about "invalid" but still
    install "valid"

* Wed Nov 28 2007 Pixel <pixel@mandriva.com> 4.10.16-1mdv2008.1
+ Revision: 113748
- 4.10.16:
- urpmi:
  o small transactions should have at least 8 packages
    (ie --split-length is now 8 by default)
  o do not do a big transaction if installing less than 20 packages
    (ie --split-level is now 1 by default)
- urpmq:
  o new option --requires-recursive (alias of option -d)
  o bugfix previous release: "urpmq --fuzzy foo" should display all "*foo*" matches

* Mon Nov 26 2007 Pixel <pixel@mandriva.com> 4.10.15-1mdv2008.1
+ Revision: 112175
- 4.10.15:
- all tools:
  o exit with code 1 after displaying usage (instead of exit code 0)
- urpmi:
  o with rsync, use --copy-links (to have the same behaviour as http/ftp, and
    so allow symlinks on the server)
  o fix "urpmi --install-src" (regression introduced in 4.10.9) (#35164)
  o fix --limit-rate (regression introduced in 4.9.12)
  o --auto-update is quite unsafe, but at least now it should be cleaner
    (ensure $urpm doesn't have media twice)

* Thu Oct 04 2007 Pixel <pixel@mandriva.com> 4.10.14-1mdv2008.0
+ Revision: 95395
- 4.10.14:
- library:
  o urpm::media::add_distrib_media: add option "only_updates" for rpmdrake

* Wed Oct 03 2007 Pixel <pixel@mandriva.com> 4.10.13-1mdv2008.0
+ Revision: 95004
- provide mandrake-mime 0.5 to fix priority-upgrade from 2007.0
- 4.10.13:
- urpmi
  o remove prefix/var/lib/rpm/__db* after installing pkgs rooted

* Thu Sep 27 2007 Pixel <pixel@mandriva.com> 4.10.12-1mdv2008.0
+ Revision: 93332
- 4.10.12:
- urpm::media::update_media:
  o ensure a second pass is done even if media has not been modified
    (useful for the %%trigger trick done in urpmi to rebuild synthesis with
    suggests)
- urpmf
  o fix -a and -o
- fix "ensure synthesis built from hdlist is rebuilt so that it has suggest flags"
  (make it work if hdlist/synthesis file has spaces)

* Mon Sep 24 2007 Pixel <pixel@mandriva.com> 4.10.11-1mdv2008.0
+ Revision: 92593
- ensure synthesis built from hdlist is rebuilt so that it has suggest flags
- 4.10.11:
- create /var/tmp in chroots too
- fixed nb.po
- perl-Test-Pod is needed for make test (thanks chipaux)

* Mon Sep 17 2007 Pixel <pixel@mandriva.com> 4.10.10-1mdv2008.0
+ Revision: 89071
- 4.10.10:
- fix using already downloaded rpms (from /var/cache/urpmi/rpms) (#33655)
- improve retrieving update descriptions API

* Thu Sep 13 2007 Pixel <pixel@mandriva.com> 4.10.9-1mdv2008.0
+ Revision: 85103
- 4.10.9:
- urpmi, urpme
  o default to selecting all the prefered packages according to installed
    locales (need perl-URPM 2.00 to work)
  o do not prompt questions if not waiting for user answer
    (for urpmi --force or urpme --force)
- urpmf
  o fix --synthesis

* Mon Sep 10 2007 Pixel <pixel@mandriva.com> 4.10.8-1mdv2008.0
+ Revision: 84103
- 4.10.8:
- urpmi
  o enhance "columns" display of packages to install (esp. fit on 80 columns)
  o do not use netrc for protocol ssh

* Fri Sep 07 2007 Pixel <pixel@mandriva.com> 4.10.7-1mdv2008.0
+ Revision: 81471
- new release, 4.10.7
- urpmi
  o fix rpmdb locking with --root
  o handle --searchmedia <media1>,...,<mediaN>
  o do auto upgrade mandriva kernels (ie remove kernel*-latest to skip.list)
  o display size that will be installed - removed with a nice message (#32022)
  o display packages which are going to installed with name-version-release
    info in columns
- urpmi, urpme
  o use best unit (KB, MB...) to display size will be installed - removed

* Tue Aug 28 2007 Pixel <pixel@mandriva.com> 4.10.6-1mdv2008.0
+ Revision: 72761
- new release, 4.10.6
- urpmi
  o fix --bug when there is no /etc/urpmi/prefer.list file
  o new option --justdb (new perl-URPM 1.76)
  o do not verify signature of .spec files (#32824)
  o handle changes in priority-upgrade list between old and new urpmi (#32925)
- urpmf
  o display "usage" when no <pattern-expression> is given (#32658)

* Sat Aug 18 2007 Pixel <pixel@mandriva.com> 4.10.5-1mdv2008.0
+ Revision: 65548
- new release, 4.10.5
- urpmi
  o keep_all_tags for now to avoid rpm saying file conflicts when the content
    is the same
  o restart after upgrading 'meta-task' because of /etc/urpmi/prefer.vendor.list

* Mon Aug 13 2007 Pixel <pixel@mandriva.com> 4.10.4-2mdv2008.0
+ Revision: 62787
- require meta-task for /etc/urpmi/prefer.vendor.list

* Mon Aug 13 2007 Pixel <pixel@mandriva.com> 4.10.4-1mdv2008.0
+ Revision: 62753
- new release, 4.10.4
- urpmi
  o bugfix 4.10.0: a circular reference was causing rpmdb to be opened many times
  o --urpmi-root: if <root>/etc/urpmi/*.list are available, use them.
    otherwise defaults to /etc/urpmi/*.list

* Mon Aug 13 2007 Thierry Vignaud <tv@mandriva.org> 4.10.3-1mdv2008.0
+ Revision: 62580
- urpmi
  o do not default to --nolock when using --root (reverting rafael
    commit on 2006-01-11 13:17)
  o do try to umount removable media when using --nolock (fixing
    rafel's commit r15048 on 2005-06-09)
  o try harder to explain why a package is removed
  o try harder to explain why we cannot select a package (eg: because
    i586 package is already installed on x86_64)

* Mon Aug 13 2007 Thierry Vignaud <tv@mandriva.org> 4.10.2-1mdv2008.0
+ Revision: 62433
- gurpmi:
  o reuse common shared code of urpmi/rpmdrake
  o umount removable media as soon as possible
  o unlock RPM & URPMI dbs locks as soon as possible like rpmdrake
- urpmi
  o when using --urpmi-root, load <root>/etc/rpm/macros (pixel)
  o enable GUIes to display already installed & not installable RPMs
  o enable GUIes to display uninstallations
- urpmi.cfg
  o really add global option no-suggests (pixel)
- kill old source

* Sun Aug 12 2007 Pixel <pixel@mandriva.com> 4.10.1-1mdv2008.0
+ Revision: 62247
- new release, 4.10.1
- library
  o urpm::select: new function get_preferred() replacing sort_choices()
    (for drakx)

* Sat Aug 11 2007 Pixel <pixel@mandriva.com> 4.10.0-1mdv2008.0
+ Revision: 61993
- new release, 4.10.0
- urpmi
  o new option --replacepkgs (same as rpm --replacepkgs) (#16112)
    (need perl-URPM 1.73)
  o fix --quiet (regression introduced in 4.9.28)
  o handle preferred choices (through --prefer, /etc/urpmi/prefer.list
    and /etc/urpmi/prefer.vendor.list)
- all tools
  o new option --wait-lock (#13025)

* Fri Aug 10 2007 Pixel <pixel@mandriva.com> 4.9.30-1mdv2008.0
+ Revision: 61515
- new release 4.9.30
- urpmi (thanks to Thierry Vignaud)
  o move some code to new module urpm::main_loop to share it with rpmdrake

* Thu Aug 09 2007 Pixel <pixel@mandriva.com> 4.9.29-2mdv2008.0
+ Revision: 60891
- we can't conflict with mandrake-mime which is required by kde on 2007.0
  (otherwise we have to disable priority-upgrade)

* Thu Aug 09 2007 Pixel <pixel@mandriva.com> 4.9.29-1mdv2008.0
+ Revision: 60822
- new release, 4.9.29
- urpmi
  o explicit error when using "urpmi ---install-src" as user with remote media
  o add support for "suggests": a newly suggested package is installed as if
    required, but one can remove it afterwards, or use --no-suggests
    (need perl-URPM 1.69)
- urpmf
  o handle --suggests

* Fri Aug 03 2007 Pixel <pixel@mandriva.com> 4.9.28-1mdv2008.0
+ Revision: 58594
- mandriva-gurpmi.desktop: make desktop-file-validate happy
- new release, 4.9.28 (need perl-URPM 1.68)
- urpmi
  o handle README.<version>.upgrade.urpmi and
    README.<version>-<release>.upgrade.urpmi: the content is displayed
    when upgrading from rpm older than <version> (#30187)
- urpmf
  o handle --license
- urpmi.update
  o handle -q option (#31890)
- urpmq
  o --whatrequires: fix skipping packages through provides provided by other
    packages, when the other package is the same pkg name (#31773)
- library
  o urpm::install: export %%readmes so that rpmdrake can access it
- add application/x-urpmi definition for gurpmi (#32139)

* Mon Jun 18 2007 Pixel <pixel@mandriva.com> 4.9.27-1mdv2008.0
+ Revision: 41003
- new release, 4.9.27
- urpmi.addmedia --distrib, urpmi/urpme/urpmf/urpmq --use-distrib
  o media.cfg per media field hdlist=hdlist_xxx.cz is not used anymore,
    xxx/media_info/hdlist.cz is used instead. To get previous behaviour, use
    option --use-copied-hdlist or use_copied_hdlist=1 in media.cfg
- urpmi
  o for long package names, ensure progression of installation (####...) is
    still properly indented (#28639)
- urpmi.addmedia
  o fix reconfig.urpmi use
- urpmi.update
  o only copy previous hdlist in cache dir for rsync, don't do it for wget/curl
    (it's useless and potentially dangerous when used with "resume")
- urpmf
  o bug fix -m (#31452)
- all tools
  o 4.9.26 is broken when downloading with wget since it creates hdlist.cz.1
    files. fixing using --force-clobber option (! need a patched wget !)
  o hide rsync errors by default to hide false positives,
    but allow getting them with --debug

* Thu Jun 14 2007 Pixel <pixel@mandriva.com> 4.9.26-1mdv2008.0
+ Revision: 39559
- new release, 4.9.26
- urpmf
  o add option --use-distrib
- urpmq
  o allow using --use-distrib as non-root
- all tools
  o don't use time-stamping when downloading with wget
    (useless and slow since it forces to download the whole directory listing)
    (as suggested by Andrey Borzenkov on cooker)

* Fri Jun 08 2007 Pixel <pixel@mandriva.com> 4.9.25-1mdv2008.0
+ Revision: 37218
- new release, 4.9.25
- all tools
  o --debug now implies --verbose
- urpmi.addmedia
  o [bugfix] fix using "with synthesis.hdlist.cz" (#31081)
  o don't overwrite existing urpmi.cfg with an empty file
    when disk is full (#30945)
- urpmi
  o prefer best architecture over exact name
    (eg: urpmi libfoo-devel prefers lib64foo-devel over libfoo-devel)
  o [bugfix] fix urpmi --parallel (#30996)
  o [bugfix] fix plural handling in "Packages foo can not be installed" (#31229)
  o fix "Argument list too long" when calling curl/wget/proz
    (things should work even in case of one big transaction) (#30848)
- urpmf
  o fix an *old* bug (since december 2002) making urpmf keeps parsed hdlist
    files in memory

* Wed May 09 2007 Pixel <pixel@mandriva.com> 4.9.24-1mdv2008.0
+ Revision: 25749
- new release, 4.9.24
- urpmi
  o display "removing package ..." when removing an obsolete or conflicting
    package (need perl-URPM 1.63), and not before
  o in verbose mode, display "removing upgraded package ..."
    (should make it more understandable by users)
- urpmi.addmedia
  o [bugfix] fix removable://... (#30257)
  o [bugfix] look for media/$media_dir/media_info/pubkey instead of
    media/$media_dir/pubkey
  o [bugfix] with --distrib, don't use previous media's pubkey if a pubkey is
    missing (eg: use pubkey_main for media "Main Updates" when
    pubkey_main_updates is missing)

* Thu May 03 2007 Pixel <pixel@mandriva.com> 4.9.23-1mdv2008.0
+ Revision: 21601
- perl-URPM 1.62 is required by urpmi 4.9.23
- new release, 4.9.23
- urpmi
  o always upgrade (-U) packages instead of installing (-i) them,
    except for inst.list packages. This change is needed to fix
    "b--obsoletes-->a and c--conflicts-->a prompting for upgrading a"
    in perl-URPM 1.61
  o fix displaying README.*urpmi when using --root or --urpmi-root
  o fix displaying README.install.urpmi when installing a package conflicting
    with an available package
  o display "removing package ..." when removing, not before.
  o display "removing package ..." when upgrading package
    (may be too verbose though)
  o display "In order to satisfy the '%%s' dependency, one of the following
    packages is needed:" so that user can understand what dependency is used
- for rpmdrake
  o make translate_why_removed() safe to call (cf bug #28613)


* Wed Mar 28 2007 Pixel <pixel@mandriva.com> 4.9.21-1mdv2007.1
+ Revision: 149186
- new release, 4.9.21
- urpmi
  o add kernel-source-latest to skip.list
    (to be coherent with other kernel*latest) (#29933)
- urpmi.addmedia
  o do display download progression by default (be coherent with other tools),
    use -q to hide it
- urpmi.update
  o do not display download progression with -q

* Thu Mar 15 2007 Pixel <pixel@mandriva.com> 4.9.20-1mdv2007.1
+ Revision: 144263
- new release, 4.9.20
- all tools
  o be failsafe when module encoding is not there
    (ie when only perl-base is installed) (#29387)
- gurpmi:
  o fix displaying size of packages
  o fix displaying only the first package in "you're about to..." dialog
  o prevent downloading/installing dialog from resizing
- urpmi-parallel-ka-run:
  o fix parsing the output of rshp2 (only rshp output was successfully parsed)

* Thu Mar 08 2007 Pixel <pixel@mandriva.com> 4.9.19-1mdv2007.1
+ Revision: 138272
- latest perl-URPM is required
- new release, 4.9.19
- urpmi
  o fix priority-upgrade broken on some x86_64 (#29125)
    (bug introduced in urpmi 4.9.11)
- gurpmi
  o use same translation routines as urpmi, fixing various encoding issues (#29248)
- urpmq
  o remove duplicated warning for "urpmq -l" when a rpm header is missing (#29174)

* Tue Mar 06 2007 Pixel <pixel@mandriva.com> 4.9.17-3mdv2007.1
+ Revision: 134098
- add BuildRequires perl-Expect (for make test)
- add BuildRequires rpmtools for make test
- new release, 4.9.17
- urpmq
  o add --whatprovides (doing same as -p) (#29175)
- urpmi
  o don't auto upgrade mandriva kernels (ie add kernel*-latest to skip.list)
  o add perl-MDV-Distribconf to priority upgrade packages
  o display translated summaries

* Fri Mar 02 2007 Pixel <pixel@mandriva.com> 4.9.16-1mdv2007.1
+ Revision: 130964
- new release, 4.9.16
- urpmi
  o fix crash asking for medium
- urpmf
  o do not display invalid error at the end when using removable media (#28905)
- urpmq
  o --whatrequires-recursive: fix debug message explaining why a package
    is added, and enhance the verbose message explaining why some package are
    skipped

  + Thierry Vignaud <tvignaud@mandriva.com>
    - do not package huge (1Mb!) ChangeLog

* Tue Feb 27 2007 Pixel <pixel@mandriva.com> 4.9.15-2mdv2007.1
+ Revision: 126242
- gzip is used in perl-URPM for synthesis and hdlist
  (not adding the require directly in perl-URPM since it can do many things
  without using gzip)
- new release, 4.9.15
- urpmi.update
  o add --probe-rpms to replace -f -f
  o -f -f should be allowed (#28500)
- urpmq
  o --whatrequires will now handle virtual package requires
    (eg: bash is now returned by "urpmq --whatrequires glibc")
    (#28367)
- german translation
  o don't use non iso-8859-15 chars otherwise perl segfaults (#28537)
    (perl bug #41442)

* Thu Jan 25 2007 Pixel <pixel@mandriva.com> 4.9.14-1mdv2007.1
+ Revision: 113401
- new release, 4.9.14
- urpmi
  o fix encoding issue with "--bug ..." introduced in previous version (#28387)
- urpmi, ...
  o workaround no locale (eg: LC_ALL=C): when encoding is "ascii",
    do not try to convert strings to this encoding, any encoding will do
    (#28367)
- urpmq
  o rename option -R into --whatrequires
  o rename option -RR into --whatrequires-recursive,
    and don't go through virtual packages which are provided by another
    package, eg: "skipping package(s) required by db1-devel via devel(libdb),
    since that virtual package is provided by libdb2-devel"
    (#27814)
  o do not document option -P (which is the default)

* Fri Jan 19 2007 Pixel <pixel@mandriva.com> 4.9.13-1mdv2007.1
+ Revision: 110622
- no need to Requires and Requires(post) the same pkg
- new release, 4.9.13
- urpmi, ...
  o fix encoding/codeset mess (using the magical
  Locale::gettext::bind_textdomain_codeset(..., "UTF-8") from new
  perl-Locale-gettext)
  o fix translating rpmlib messages (using URPM::bind_rpm_textdomain_codeset())
- gurpmi2
  o do display installation failed on file conflicts (#22131)
- urpmi.addmedia
  o do not display in clear text the password (when using -v or --debug)
- urpmq
  o when using synthesis do not download packages to get information.
    before this modification, it was downloaded iff one medium was using hdlist (#16772)
  o when using synthesis fix using local rpms to get information
    before this modification, local rpm was used iff one medium was using hdlist
  o display a warning about no hdlist only for needed media,
    adapt the warning to the option (for "-i", synthesis can still help),
    and tell which rpms and impacted
- we really want Requires(post), not Requires(pre)
- requires latest perl-Locale-gettext and perl-URPM

  + Thierry Vignaud <tvignaud@mandriva.com>
    - require new enough Locale::Gettext for better i18n management
    - fix requires (s/pre/post/)

* Wed Jan 10 2007 Pixel <pixel@mandriva.com> 4.9.12-1mdv2007.1
+ Revision: 107220
- new release, 4.9.12
- urpmi
  o fix handling removable media (bug introduced in 4.9.x) (#27854)
  o with "-v", display the package file copied to disk
  o use P (ie ngettext) to handle plurals
  o re-allow "urpmi --clean" with no arguments
    (broken on january 2006, commit r36390) (#27747)
  o be more verbose with "-v"
- urpmi, urpmq, urpmf
  o "--media foo" and "--searchmedia foo" use medium "foo"
    even if "foo" is flagged "ignore" (#27745)
- urpmi.addmedia
  o new option "--probe-rpms" which replaces "-f -f"
  o fix using dir "/foo/bar boo" and no hdlist (using *.rpm)
  o when using "--distrib <url>", have "xxx" instead of "xxx1"
    for the medium name (eg: "Main" instead of "Main1")
  o when using --distrib, add noauto media with flag ignore
    so that someone can easily use them by removing ignore
    (nb: debug_for and srpm media are not added though)
    (cf bug #28050)
- add NEWS file
- add BuildRequires perl-MDV-Distribconf for tests (thanks to spturtle)

* Tue Dec 12 2006 Pixel <pixel@mandriva.com> 4.9.11-1mdv2007.1
+ Revision: 95344
- new release, 4.9.11
- urpmi
  o when "urpmi --auto-select" needs to restart urpmi because of a
    priority-upgrade, ensure it doesn't prompt an unneeded choice before
    restarting (#27527)
    (nb: the problem can still occur on "urpmi rpmdrake")
- urpmi.removedia
  o "urpmi.removedia -a" when urpmi.cfg has no entry still warn the user,
     but exits with status 0

* Thu Dec 07 2006 Pixel <pixel@mandriva.com> 4.9.10-1mdv2007.1
+ Revision: 91953
- bug fix release:
- urpmi.addmedia
  o fix using "--virtual --distrib ..."

* Wed Dec 06 2006 Pixel <pixel@mandriva.com> 4.9.9-1mdv2007.1
+ Revision: 91815
- 4.9.9
- urpmi
  o fix "rpmdb: environment reference count went negative"
    when syslog service is down
  o fix having more than "hdlist" flag in urpmi.cfg
- gurpmi2 (and rpmdrake)
  o fix crash when syslog service is down (#26256)

* Wed Dec 06 2006 Pixel <pixel@mandriva.com> 4.9.8-1mdv2007.1
+ Revision: 91685
- 4.9.8
- urpmi.addmedia, urpmi
  o use "hdlist" just like "synthesis" when forcing only hdlist usage
  o "hdlist" is valid with "virtual"
- urpmi
  o don't say "Package foo-1.1 already installed"
    when in fact it is "Package foo-1.2 already installed".
    Still display "Package foo-1.1 can not be installed" until we can do
    better (#27176)
- gurpmi (tvignaud)
  o don't ignore exceptions in callbacks
  o fix crash and really lock the urpm db

* Mon Dec 04 2006 Pixel <pixel@mandriva.com> 4.9.7-1mdv2007.1
+ Revision: 90447
- 4.9.7, bug fix release
- urpmi.addmedia
  o fix --probe-hdlist
  o fix "... with hdlist.cz" (only "... with synthesis.hdlist.cz" was working)
- urpmi
  o add the long version of -q/-v (ie --quiet/--verbose)
  o --quiet is really quiet

* Fri Dec 01 2006 Pixel <pixel@mandriva.com> 4.9.6-1mdv2007.1
+ Revision: 89835
- 4.9.6, bug fix release
- urpmi.addmedia:
  o fix downloading synthesis which is done twice when remote
  o fix downloading pubkey in media_info/
- urpmf:
  o handle --urpmi-root

* Thu Nov 30 2006 Pixel <pixel@mandriva.com> 4.9.5-1mdv2007.1
+ Revision: 89296
- new release
- all tools:
  o new option --urpmi-root that is similar to --root but also use rooted
    urpmi db
- urpmi:
  o handle buggy "list: xxx" in urpmi.cfg (when the list can't be found)
  o handle no "synthesis" together with "with_hdlist: synthesis.hdlist.cz"
- urpmi.cfg:
  o new per-medium field "media_info_dir:" which replaces "with_hdlist:" in
    most cases. It allows using either hdlist & synthesis when nor
    "hdlist:" nor "synthesis" is set
- urpmi.update:
  o not so verbose by default, only display
    'medium "foo" is up-to-date' or 'medium "foo" updated'
- urpmi.removemedia:
  o not so verbose by default, only display 'removing medium "foo"'
  o do not allow both "-a" and <name>, fix usage
- urpmi.addmedia:
  o not so verbose by default, only display 'adding medium "foo"'
  o do not add "hdlist: hdlist.<name>.cz" lines in urpmi.cfg,
    compute it from <name> (one can still enforce a file name)
  o do not default to --probe-synthesis but use both hdlist/synthesis

* Fri Nov 24 2006 Pixel <pixel@mandriva.com> 4.9.4-1mdv2007.1
+ Revision: 87093
- urpmi.addmedia:
  o fix random ordering of media (using --distrib on a non-remote medium)
  o now inserting non-remote medium after first non-remote medium
    (instead of adding it as first medium)
- urpmi, urpme, urpmq:
  o add option --probe-synthesis (allowed with --use-distrib)

* Fri Nov 24 2006 Pixel <pixel@mandriva.com> 4.9.3-1mdv2007.1
+ Revision: 86975
- bug fix release:
- fix handling multiple virtual hdlist files
  (the second pass was not done...)

* Fri Nov 24 2006 Pixel <pixel@mandriva.com> 4.9.2-1mdv2007.1
+ Revision: 86883
- bug fix release:
- /foo/chroot_tmp/... is not a url with protocol /foo/chroot

* Thu Nov 23 2006 Pixel <pixel@mandriva.com> 4.9.1-1mdv2007.1
+ Revision: 86698
- add module urpm/lock.pm
- 4.9.1
- cleanup locks handling, log locking, and don't say "urpmi database locked"
  when it's the rpm database that is locked
- urpmi: add --nokeep (which overrides urpmi.cfg global option "keep")

* Wed Nov 22 2006 Pixel <pixel@mandriva.com> 4.9.0-1mdv2007.1
+ Revision: 86106
- release 4.9.0
- urpmi:
  o don't fork on multiple transactions
  o fix buggy print "::logger_id::" (#27026)
- gurpmi2 (tvignaud):
  o fix unvisible content
  o prevent a dialog to have a height of several scores of thousands pixels
  o add support of --root
- urpmi.update:
  o don't write urpmi.cfg unless really needed
  o don't write md5sum in urpmi.cfg (bugfix)
- urpmi.addmedia:
  o drop support for "list" file
    (now you must have a hdlist/synthesis on remote server)
  o drop support for searching recursively rpms when there is no
    hdlist/synthesis. Only search in given directory (ie $url/*.rpm)
  o do not use list.<media_name> to store passwords, use /etc/urpmi/netrc
    instead. Also do have the url in urpmi.cfg, only the password is removed
  o change the format of list.<media_name>, it contains only rpm files
    relative to the medium url
  o deprecate "... with <relative hdlist/synthesis>". It is not useful anymore
    (nb: if you want to force using hdlist or synthesis, use --probe-hdlist or
    --probe-synthesis)
  o don't write urpmi.cfg twice
  o do not look for hdlist/synthesis in ../media_info/hdlist$suffix.cz (nb:
    with media.cfg, it will still use hdlist from media/media_info/, but it
    will simply use the hdlist$suffix.cz given by media.cfg )
  o --norebuild is by default (and deprecated): when the local
    hdlist/synthesis is buggy, do not discard it and go searching for *.rpm.
    Make it an error instead
  o fix building synthesis when using *.rpm (ie no hdlist/synthesis)
- urpmi.removemedia: much faster (since it doesn't parse hdlist/synthesis anymore)
- handle "empty" hdlist/synthesis
- generate names.<media_name> only when the medium is created/updated
- major splitting of urpm.pm in many modules
- major splitting of functions in smaller functions
  (eg: update_media was 988 lines long, has been splitted in functions shorter
  than 105 lines)
- big code cleanup/rework
- perl_checker compliance (very useful for such big code rework)

* Tue Nov 07 2006 Pixel <pixel@mandriva.com> 4.8.29-1mdv2007.1
+ Revision: 77291
- urpmi
  - when using "-v", display which packages+versions urpmi will try to install
  - replace the dreaded "The package(s) are already installed" with:
    - "Packages are up to date" for --auto-select
    - "Package foo-1.1-1mdv.i586 is already installed" when asking to install package foo
  - ask user before installing a package that matches part of the name
- urpmf
  - 25%% speedup when searching files
  - indent %%description and do not display on first line.
    this makes the output of --description much more readable
  package names
- gurpmi (tvignaud):
  - add support of --root for gurpmi
  - prevent a dialog to have a height of several scores of thousands pixels
- urpmi.addmedia (nanardon): askmedia and suppl option in hdlists where not
  per media option but undocumented global option for DrakX
- various code cleanup (and perl_checker compliance)

* Thu Sep 21 2006 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.28-1mdv2007.0
+ Revision: 62430
- Fix a bug in urpmi.addmedia for removable media

* Wed Sep 20 2006 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.27-1mdv2007.0
+ Revision: 62298
- Update tarball
- . Hack to minimize file descriptor leak when upgrading from 2006
  . Don't read ~/.curlrc (Nicolas Melay)
  . Don't ignore other media when using --auto-update

* Wed Sep 13 2006 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.26-1mdv2007.0
+ Revision: 60978
- Fix bug in handling updates_for keyword in media.cfg

* Tue Sep 12 2006 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.25-1mdv2007.0
+ Revision: 60899
- . Add support for updates_for keyword in media.cfg
  . translation updates

* Wed Sep 06 2006 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.24-1mdv2007.0
+ Revision: 59961
- urpmi 4.8.24 :
  . fixes gurpmi file association
  . output bugs fixed
  . urpmi -q is more quiet
  . translations updated
  . reap ssh processes
- Fix the new menu so gurpmi is run when double-clicking on an rpm
  (bug #25148)

* Sat Aug 12 2006 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.23-1mdv2007.0
+ Revision: 55635
- XDG migration
- New manpage: urpmihowto
- Misc. doc fixes
- Use --anyauth with curl downloads
- urpmi.removemedia and urpmi.addmedia now return a proper exit status
- bash completions fixes by Guillaume Rousse
- Reapply revision #55291
- Import urpmi

* Wed Jul 12 2006 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.22-1mdv2007.0
- Update docs and translations
- Allow to install deps of an srpm via rurpmi (Pascal Terjan)
- Add an -f option to rpm-find-leaves

* Wed Jun 21 2006 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.21-1mdv2007.0
- New command rurpme
- Forbid rurpmi --noscripts
- Don't ignore unselected media with --auto-update
- Remove old rpmdb log files at restart

* Tue Jun 13 2006 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.20-1mdv2007.0
- New options to urpmi.addmedia: --interactive and --all-media (Olivier Thauvin)
- urpmi.addmedia --distrib now uses media.cfg instead of hdlists (Olivier Thauvin)
- Use global proxy settings when adding a media (Vincent Panel, bug #22000)
- New urpmf option: -I. Also, make it handle "--" on command line
- Don't restart urpmi when started with --root (bug #22509)
- Misc. fixes to urpmi --bug
- Misc. fixes to gurpmi
- Don't sync to disk when closing rpmdb
- Doc fixes

* Fri Apr 21 2006 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.19-1mdk
- Fix running rurpmi with curl/wget, could have tainting errors
- Repackaging counter is prettier
- Several fixes in gurpmi by Thierry Vignaud

* Thu Apr 06 2006 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.18-1mdk
- Fix noisy output on http media update
- Translation updates

* Tue Apr 04 2006 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.17-1mdk
- urpmi.recover --list-safe
- proper handling of SIGINT in urpmi.addmedia
- make gurpmi clean the download cache
- fix urpmq --synthesis
- make gurpmi test directly if file argument exists (Warly)
- fix ssh download as non-root (Michael Scherer)
- print more reports on download errors
- doc updates

* Wed Mar 22 2006 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.16-1mdk
- Fix again transaction counter (and make it prettier)
- More docs

* Tue Mar 21 2006 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.15-1mdk
- Lock the urpmi db when adding a media
- Correct transaction count, even when repackaging, and better readability
- Enhance a couple of error messages

* Mon Mar 20 2006 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.14-1mdk
- Add --auto-select, --media and --searchmedia options to gurpmi
- Various gurpmi fixes (Thierry Vignaud)
- Fix installation of srpms by urpmi
- Portability enhancements (Buchan Milne)
- Warn on downloader change (Michael Scherer)
- Reuse ssh connection if possible (Michael Scherer)
- Add French man page (Christophe BerthelÃ©)

* Fri Mar 03 2006 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.13-1mdk
- Doc
- Fix cache cleanup (bug #17913)
- Require latest perl-URPM

* Tue Feb 28 2006 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.12-1mdk
- Less verbosity with urpmi -q
- Translation and doc updates
- avoid a perl warning in urpmi.recover

* Fri Feb 17 2006 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.11-1mdk
- New option, urpmi.recover --disable
- Docs fixes
- Miscellaneous bash completions fixes
- Let "ignoresize" be configurable in urpmi.cfg

* Tue Feb 14 2006 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.10-1mdk
- New tool: urpmi.recover (in its own rpm)
- urpmi: clean cache more aggressively (bug #17913)
- Don't log to /var/log/urpmi.log anymore, use syslog
- urpme and urpmi.recover use syslog too
- New config file urpmi.recover.macros
- Add new option --repackage to urpmi and urpme
- Add new option --ignorearch to urpmi and urpmq
- Fix --no-verify-rpm with gurpmi
- Fix usage of global urpmi.cfg options in gurpmi
- Various useability fixes in urpme
- Doc improvements

* Thu Feb 02 2006 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.9-1mdk
- Fix call of --limit-rate option with recent curls
- Fix some explanations on biarch environments
- Fix error recovery on download of description files (Shlomi Fish)
- Docs and translation updates

* Wed Jan 25 2006 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.8-1mdk
- urpmi can now install specfile dependencies
- Escape media names in urpmq --dump-config (Michael Scherer)
- Require latest perl-URPM
- Better docs

* Fri Jan 13 2006 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.7-1mdk
- Allow to install SRPMs as a non-root user (Pascal Terjan)
- Better diagnostics in a few cases
- Doc improvements; document --nolock option
- Don't lock when installing into a chroot
- Code cleanup in download routines
- Fix BuildRequires

* Wed Jan 04 2006 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.6-1mdk
- rurpmi now doesn't install packages with unmatching signatures
- Fix MD5SUM bug
- Count correctly transactions even when some of them failed
- Don't update media twice when restarting urpmi

* Fri Dec 23 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.5-1mdk
- New urpmi option, --auto-update
- New urpme option, --noscripts
- Fix BuildRequires

* Thu Dec 08 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.4-1mdk
- urpmi.addmedia doesn't reset proxy settings anymore
- urpmi.removemedia now removes corresponding proxy settings
- Fix installation of packages that provide and obsolete older ones
- Remove the urpmq --headers option

* Mon Dec 05 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.3-1mdk
- New configuration option, default-media
- New options --wget-options, --curl-options and --rsync-options
- Fix /proc/mount parsing to figure out if a fs is read-only (Olivier Blin)
- Use a symlink for rpm-find-leaves (Thierry Vignaud)
- Better error checking when generating names file
- Manpage updates
- Translation updates
- Bash completion updates

* Fri Nov 25 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.2-1mdk
- Now build urpmi using MakeMaker.
- Some basic regression tests.
- Non-english man pages are not installed by default anymore. They were not at
  all up to date with the development of the last years.
- English man pages are now in POD format.
- Correctly search for package names that contain regex metacharacters.

* Thu Nov 17 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.1-2mdk
- urpmi: Move summary of number of packages / size installed at the end
- Don't require ka-run directly, use virtual package parallel-tools
- Message updates

* Thu Nov 17 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.1-1mdk
- Display README.urpmi only once
- Add a --noscripts option to urpmi
- Install uninstalled packages as installs, not as upgrades
- Make urpmi::parallel_ka_run work with taktuk2

* Mon Nov 14 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.8.0-1mdk
- Allow to put rpm names on the gurpmi command-line
- Make --no-verify-rpm work for gurpmi
- Improve some error messages in urpmi and gurpmi (bug #19060)
- Fail earlier and more aggressively when downloading fails
- Fix download with rsync over ssh
- Use the --no-check-certificate option for downloading with wget
- Use MDV::Packdrakeng; avoid requiring File::Temp, MDK::Common and packdrake
- rpmtools is no longer a PreReq
- Build process improvements
- Reorganize urpmq docs; make urpmq more robust; make urpmq require less locks

* Thu Oct 27 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.7.18-1mdk
- gurpmi now expands .urpmi files given on command-line, just like urpmi
- urpmi.addmedia --raw marks the newly added media as ignored

* Fri Oct 21 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.7.17-1mdk
- Complete urpmf overhaul
- Fix verbosity of downloader routines

* Wed Oct 12 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.7.16-1mdk
- New urpmi option --ignoresize
- urpmq, urpmi.addmedia and urpmi.update now abort on unrecognized options
- Add glibc to the priority upgrades

* Thu Sep 15 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.7.15-1mdk
- Fix --gui bug with changing media
- Message updates

* Thu Sep 08 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.7.14-1mdk
- Optimize utf-8 operations
- Don't decode utf-8 text when the locale charset is itself in utf-8
- Message updates

* Tue Sep 06 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.7.13-1mdk
- Really make Date::Manip optional

* Fri Sep 02 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.7.12-1mdk
- Fix urpmi --gui when changing CD-ROMs
- Fix a case of utf-8 double encoding

* Thu Sep 01 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.7.11-3mdk
- suppress wide character warnings

* Wed Aug 31 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.7.11-2mdk
- message updates
- decode utf-8 on output

* Sat Aug 20 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.7.11-1mdk
- MD5 for hdlists weren't checked with http media
- Don't print twice unsatisfied packages
- gurpmi: allow to cancel when gurpmi asks to insert a new media

* Tue Jul 19 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.7.10-2mdk
- Message and manpage updates

* Sat Jul 02 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.7.10-1mdk
- Fix rurpmi --help
- Patch by Pascal Terjan for bug 16663 : display the packages names urpmi
  guessed when it issues the message 'all packages are already installed'
- Allow to cancel insertion of new media in urpmi --gui
- Message updates

* Thu Jun 30 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.7.9-1mdk
- Add rurpmi, an experimental restricted version of urpmi (intended
  to be used by sudoers)

* Wed Jun 29 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.7.8-1mdk
- Allow to select more than one choice in alternative packages to be installed
  by urpmi
- Add LDAP media at the end
- Doc and translations updated

* Tue Jun 14 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.7.7-1mdk
- Fix documentation for urpmq --summary/-S and urpmf -i (Olivier Blin)
- urpmq: extract headers only once

* Sat Jun 11 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.7.6-1mdk
- Fix bug on urpmi-parallel-ssh on localhost with network media

* Fri Jun 10 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.7.5-1mdk
- urpmi-parallel-ssh now supports 'localhost' in the node list and is a bit
  better documented

* Wed Jun 08 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.7.4-1mdk
- Implement basic support for installing delta rpms
- Fix bug #16104 in gurpmi: choice window wasn't working
- Implement -RR in urpmq to search through virtual packages as well (bug 15895)
- Manpage updates

* Wed May 18 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.7.3-2mdk
- Previous release was broken

* Wed May 18 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.7.3-1mdk
- Introduce urpmi-ldap (thanks to Michael Scherer)
- Don't pass bogus -z option to curl
- Add descriptions to the list of rpms to be installed in gurpmi

* Thu May 05 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.7.2-1mdk
- Adaptations for rpm 4.4.1 (new-style key ids)
- Add a "nopubkey" global option in urpmi.cfg and a --nopubkey switch to
  urpmi.addmedia

* Fri Apr 29 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.7.1-1mdk
- Fix a long-standing bug when copying symlinked hdlists over nfs
- Minor rewrites in the proxy handling code

* Wed Apr 27 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 4.7.0-1mdk
- urpmi.addmedia: new option --raw
- remove time stamps from rewritten config files
- new config option: "prohibit-remove" (Michael Scherer)
- urpmi: don't remove basesystem or prohibit-remove packages when installing
  other ones
- new config option: "static" media never get updated
- gurpmi: correctly handle several rpms at once from konqueror
- urpmi: new option --no-install (Michael Scherer)
- urpmi: allow relative pathnames in --root (Michael Scherer)
- urpmi: handle --proxy-user=ask, so urpmi will ask user for proxy credentials
- improve man pages
- po updates

* Tue Apr 12 2005 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.24-3mdk
- Change the default URL for the mirrors list file

* Thu Apr 07 2005 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.24-2mdk
- po updates

* Thu Mar 31 2005 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.24-1mdk
- More fixes related to ISO and removable media

* Fri Mar 25 2005 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.23-5mdk
- Fixes related to ISO media

* Thu Mar 24 2005 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.23-4mdk
- Disable --gui option when $DISPLAY isn't set

* Wed Mar 23 2005 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.23-3mdk
- Add a --summary option to urpmq (Michael Scherer)

* Fri Mar 11 2005 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.23-2mdk
- error checking was sometimes not enough forgiving

* Thu Mar 10 2005 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.23-1mdk
- new urpmi option, --retry
- better system error messages

* Wed Mar 09 2005 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.22-2mdk
- Fix requires on perl-Locale-gettext
- Warn when a chroot doesn't has a /dev

* Tue Mar 08 2005 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.22-1mdk
- Fix addition of media with passwords
- More verifications on local list files

* Mon Mar 07 2005 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.21-1mdk
- Output log messages to stdout, not stderr.
- Fix spurious tags appearing in urpmi.cfg
- Documentation nits and translations
- Menu fix for gurpmi (Frederic Crozat)

* Fri Feb 25 2005 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.20-1mdk
- Output takes now into account the locale's charset
- Don't require drakxtools anymore
- Fix log error in urpmi-parallel
- Docs, language updates

* Mon Feb 21 2005 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.19-1mdk
- Document /etc/urpmi/mirror.config, and factorize code that parses it

* Thu Feb 17 2005 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.18-1mdk
- Work around bug 13685, bug in display of curl progress
- Fix bug 13644, urpmi.addmedia --distrib was broken
- Remove obsoleted and broken --distrib-XXX command-line option

* Wed Feb 16 2005 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.17-1mdk
- Remove curl 7.2.12 bug workaround, and require at least curl 7.13.0
- Fix parsing of hdlists file when adding media with --distrib

* Mon Feb 14 2005 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.16-2mdk
- Don't call rpm during restart to avoid locking

* Mon Feb 14 2005 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.16-1mdk
- Patch by Michael Scherer to allow to use variables in media URLs
- Fix retrieval of source packages (e.g. urpmq --sources) with alternative
  dependencies foo|bar (Pascal Terjan)
- Fix --root option in urpme
- Require latest perl-URPM

* Fri Feb 04 2005 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.15-1mdk
- Add ChangeLog in docs
- Message updates
- gurpmi now handles utf-8 messages
- print help messages to stdout, not stderr
- rpm-find-leaves cleanup (Michael Scherer)
- man page updates

* Mon Jan 31 2005 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.14-1mdk
- urpmi.addmedia and urpmi now support ISO images as removable media
- "urpmq -R" will now report far less requires, skipping virtual packages.
- Improve bash-completion for media names, through new options to urpmq
  --list-media (by Guillaume Rousse)

* Tue Jan 25 2005 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.13-1mdk
- urpme now dies when not run as root
- improve error reporting in urpmi-parallel
- perl-base is no longer a priority upgrade by default
- factor code in gurpmi.pm; gurpmi now supports the --no-verify-rpm option
- "urpmi --gui" will now ask with a GUI popup to change media. Intended to be
  used with --auto (so other annoying dialogs are not shown).

* Wed Jan 19 2005 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.12-1mdk
- perl-base is now a priority upgrade by default
- gurpmi has been split in two programs, so users can save rpms without being root

* Mon Jan 10 2005 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.11-1mdk
- Add an option to urpmi, --expect-install, that tells urpmi to return with an
  exit status of 15 if it installed nothing.
- Fix 'urpmf --summary' (Michael Scherer)
- Language updates

* Thu Jan 06 2005 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.10-1mdk
- Langage updates
- urpmi now returns a non-zero exit status il all requested packages were
  already installed
- fix a small bug in urpmq with virtual media (Olivier Blin)
- fail if the main filesystems are mounted read-only

* Fri Dec 17 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.9-1mdk
- Fix urpmi --skip
- Tell number of packages that will be removed by urpme
- Remove gurpm module, conflict with older rpmdrakes

* Mon Dec 13 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.8-1mdk
- Adding a media should not fail when there is no pubkey file available
  (bug #12646)
- Require packdrake
- Can't drop rpmtools yet, urpmq uses rpm2header

* Fri Dec 10 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.7-1mdk
- Fix a problem in finding pubkeys for SRPM media.
- Fix a problem in detecting download ends with curl [Bug 12634]

* Wed Dec 08 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.6-2mdk
- Improvements to gurpmi: scrollbar to avoid windows too large, interface
  refreshed more often, less questions when unnecessary, fix --help.

* Tue Dec 07 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.6-1mdk
- gurpmi has been reimplemented as a standalone gtk2 program.
- As a consequence, urpmi --X doesn't work any longer.

* Fri Dec 03 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.5-1mdk
- Add --ignore and -­no-ignore options to urpmi.update
- Reduce urpmi redundant verbosity

* Thu Dec 02 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.4-4mdk
- Minor fix in urpmi.addmedia (autonumerotation of media added with --distrib)

* Wed Dec 01 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.4-3mdk
- Internal API additions
- urpmi wasn't taking into account the global downloader setting

* Tue Nov 30 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.4-2mdk
- Fix package count introduced in previous release

* Mon Nov 29 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.4-1mdk
- From now on, look for descriptions files in the media_info subdirectory.
  This will be used by the 10.2 update media.
- Recall total number of packages when installing.

* Fri Nov 26 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.3-1mdk
- urpmq -i now works as non root
- translations and man pages updated
- more curl workarounds

* Thu Nov 25 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.2-1mdk
- when passing --proxy to urpmi.addmedia, this proxy setting is now saved for the
  new media
- New option --search-media to urpmi and urpmq (Olivier Thauvin)
- work around a display bug in curl for authenticated http sources
- when asking for choices, default to the first one

* Fri Nov 19 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6.1-1mdk
- reconfig.urpmi on mirrors must now begin with a magic line
- don't create symlinks in /var/lib/urpmi, this used to mess up updates
- warn when MD5SUM file is empty/malformed
- use proxy to download mirror list
- Cleanup text mode progress output

* Fri Nov 12 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6-2mdk
- New error message: "The following packages can't be installed because they
  depend on packages that are older than the installed ones"

* Tue Nov 09 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.6-1mdk
- New option --norebuild to urpmi, urpmi.update and urpmi.addmedia.
- New --strict-arch option to urpmi
- Fix ownership of files in /var/lib/urpmi
- Fix bash completion for media names with spaces (Guillaume Rousse)
- Fix parallel_ssh in non-graphical mode
- Small fixes for local media built from directories containing RPMs
- Fix search for source rpm by name
- Translation updates, man page updates, code cleanup

* Thu Sep 30 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-28mdk
- New urpmf option, -m, to get the media in which a package is found
- Silence some noise in urpmq

* Wed Sep 29 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-27mdk
- Change description
- Add a "--" option to urpmi.removemedia
- Better error message in urpmi.update when hdlists are corrupted

* Sat Sep 18 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-26mdk
- urpmi.addmedia should create urpmi.cfg if it doesn't exist.

* Wed Sep 15 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-25mdk
- Don't print the urpmf results twice when using virtual media.
- Translations updates.

* Fri Sep 10 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-24mdk
- Remove deprecation warning.
- Translations updates.

* Fri Sep 03 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-23mdk
- Handle new keywords in hdlists file.
- Translations updates.

* Tue Aug 31 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-22mdk
- Fix download with curl with usernames that contains '@' (for mandrakeclub)
- Make the --probe-synthesis option compatible with --distrib in urpmi.addmedia.
- Re-allow transaction split with --allow-force or --allow-nodeps

* Thu Aug 26 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-21mdk
- new --root option to rpm-find-leaves.pl (Michael Scherer)
- add timeouts for connection establishments
- Language and manpages updates (new manpage, proxy.cfg(5))

* Thu Aug 12 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-20mdk
- Language updates
- Fix urpmi.addmedia --distrib with distribution CDs
- Fix taint failures with gurpmi
- Display summaries of packages when user is asked for choices (Michael Scherer)
- Update manpages

* Sat Jul 31 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-19mdk
- Add --more-choices option to urpmi
- Fix urpmi --excludedocs
- Make urpmi.addmedia --distrib grok the new media structure
- and other small fixes

* Wed Jul 28 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-18mdk
- Better error handling for copy failures (disk full, etc.)
- Better handling of symlinks (Titi)
- New noreconfigure flag in urpmi.cfg: ignore media reconfiguration (Misc)
- More robust reconfiguration
- Preserve media order in urpmi.cfg, add local media at the top of the list
- file:/// urls may now be replaced by bare absolute paths.
- New urpmq option: -Y (fuzzy, case-insensitive)
- New options for urpmi.addmedia, urpmi.removemedia and urpmi.update:
  -q (quiet) and -v (verbose).
- Updated bash completion.
- Message and documentation updates.

* Sat Jul 24 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-17mdk
- Make --use-distrib support new media layout.
- Update manpages.

* Fri Jul 23 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-16mdk
- Automagically reconfigure NFS media as well. (duh.)

* Wed Jul 21 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-15mdk
- Support for automatic reconfiguration of media layout
- Remove setuid support
- Minor fixes and language updates

* Tue Jul 13 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-14mdk
- Simplified and documented skip.list and inst.list
- Add an option -y (fuzzy) to urpmi.removemedia

* Sat Jul 10 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-13mdk
- Support for README.*.urpmi
- add a --version command-line argument to everything
- Deleting media now deletes corresponding proxy configuration
- Code cleanups

* Tue Jul 06 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-12mdk
- Disallow two medias with the same name
- urpmi.removemedia no longer performs a fuzzy match on media names
- gettext is no longer required

* Thu Jul 01 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-11mdk
- Methods to change and write proxy.cfg
- Language updates

* Wed Jun 30 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-10mdk
- Rewrite the proxy.cfg parser
- Let the proxy be settable per media (still undocumented)

* Tue Jun 29 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-9mdk
- Rewrite the urpmi.cfg parser
- Make the verify-rpm and downloader options be settable per media in urpmi.cfg

* Thu Jun 24 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-8mdk
- Emergency fix on urpmi.update

* Thu Jun 24 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-7mdk
- Message and man page updates
- Minor fixes

* Fri May 28 2004 Stefan van der Eijk <stefan@eijk.nu> 4.5-6mdk
- fixed Fedora build (gurmpi installed but unpackaged files)

* Sat May 22 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-5mdk
- locale and command-line fixes
- urpmf now warns when no hdlist is used
- improve docs, manpages, error messages
- urpmi.addmedia doesn't search for hdlists anymore when a 'with' argument
  is provided

* Wed May 05 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-4mdk
- urpmi.addmedia no longer probes for synthesis/hdlist files when a
  "with" argument is provided
- gurpmi was broken
- skip comments in /etc/fstab
- better bash completion (O. Blin)
- fix rsync download (O. Thauvin)

* Thu Apr 29 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-3mdk
- Fix message output in urpme
- Fix input of Y/N answers depending on current locale

* Thu Apr 29 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-2mdk
- Bug fixes : locale handling, command-line argument parsing
- Add new French manpages from the man-pages-fr package

* Tue Apr 27 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 4.5-1mdk
- Refactorization, split code in new modules, minor bugfixes

