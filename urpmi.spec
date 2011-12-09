%bcond_without	gurpmi

Name:		urpmi
Version:	6.68
Release:	%mkrel 7
Summary:	Command-line software installation tools
Group:		System/Configuration/Packaging
License:	GPLv2+
Source0:	%{name}-%{version}.tar.xz
Patch0:		urpmi.rsync.patch
Patch1:		urpmi.urpme-lock.patch
Patch2:		urpmi-inst-list.patch
Patch3:		urpmi-doc-caption.patch
Patch4:		urpmi-errcode-unselected.patch
URL:		http://wiki.mandriva.com/en/Tools/urpmi
Requires:	webfetch eject gnupg
Requires(post):	perl-Locale-gettext
Requires(post):	perl-URPM >= 4.33
# gzip is used in perl-URPM for synthesis and hdlist
Requires(post):	gzip
Requires:	genhdlist2
Requires:	perl-Time-ZoneInfo
Requires:	perl-Filesys-Df
Requires:	meta-task
Suggests:	perl-Hal-Cdroms
Suggests:	aria2
BuildRequires:	bzip2-devel
BuildRequires:	gettext intltool
BuildRequires:	perl
BuildRequires:	perl-File-Slurp
BuildRequires:	perl(Net::LDAP)
BuildRequires:	perl-URPM
BuildRequires:	perl-MDV-Packdrakeng
BuildRequires:	perl-MDV-Distribconf
BuildRequires:	perl(MDV::Distribconf::Build)
BuildRequires:	perl-Locale-gettext
BuildRequires:  perl_checker
# for make test:
BuildRequires:	perl-Test-Pod
BuildRequires:	perl-XML-LibXML
BuildRequires:  glibc-static-devel
BuildRequires:  perl-Net-Server
# for genhdlist in make test:
BuildRequires:  rpmtools
BuildRequires:  perl-Expect
BuildArch:	noarch

%description
urpmi is Mandriva Linux's console-based software installation tool. You can
use it to install software from the console in the same way as you use the
graphical Install Software tool (rpmdrake) to install software from the
desktop. urpmi will follow package dependencies -- in other words, it will
install all the other software required by the software you ask it to
install -- and it's capable of obtaining packages from a variety of media,
including the Mandriva Linux installation CD-ROMs, your local hard disk,
and remote sources such as web or FTP sites.

%if %{with gurpmi}
%package -n	gurpmi
Summary:	User mode rpm GUI install
Requires:	urpmi >= %{EVRD}
Requires:	usermode usermode-consoleonly
Obsoletes:	grpmi
Provides:	grpmi
Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils

%description -n	gurpmi
gurpmi is a graphical front-end to urpmi.
%endif

%package	parallel-ka-run
Summary:	Parallel extensions to urpmi using ka-run
Requires:	urpmi >= %{EVRD}
Requires:	parallel-tools

%description	parallel-ka-run
urpmi-parallel-ka-run is an extension module to urpmi for handling
distributed installation using ka-run or Taktuk tools.

%package	parallel-ssh
Summary:	Parallel extensions to urpmi using ssh and scp
Requires:	urpmi >= %{EVRD} openssh-clients perl

%description	parallel-ssh
urpmi-parallel-ssh is an extension module to urpmi for handling
distributed installation using ssh and scp tools.

%package	ldap
Summary:	Extension to urpmi to specify media configuration via LDAP
Requires:	urpmi >= %{EVRD}
Requires:	openldap-clients

%description	ldap
urpmi-ldap is an extension module to urpmi to allow to specify
urpmi configuration (notably media) in an LDAP directory.

%package	dudf
Summary:	Extension to urpmi to handle dudf generation and upload
Requires:	urpmi >= %{EVRD}
Requires:	perl-dudfrpmstatus
BuildRequires:	perl-dudfrpmstatus
BuildRequires:	perl-XML-Writer
BuildRequires:	perl-Data-UUID
BuildRequires:	perl-IO-Compress

%description	dudf
urpmi-dudf is an extension module to urpmi to allow urpmi to generate
and upload dudf error files. This is a part of the Europeen Mancoosi project,
a project to enhance Linux Package Management. See http://www.mancoosi.org/

%prep
%setup -q

# urpmi.rsync.patch
%patch0 -p1

# urpmi.urpme-lock.patch
%patch1 -p0

# urpmi-inst-list.patch
%patch2 -p1

# urpmi-doc-caption.patch
%patch3 -p1

# urpmi-errcode-unselected.patch
%patch4 -p1

%build
%{__perl} Makefile.PL INSTALLDIRS=vendor \
%if %{with gurpmi}
    --install-gui \
%endif
    --install-po
%{__make}

%check
%{__make} test

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
mkdir -p %{buildroot}%{_datadir}/applications
cp -a gurpmi.desktop %{buildroot}%{_datadir}/applications/mandriva-gurpmi.desktop
%endif

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

%find_lang %{name}

%preun
if [ "$1" = "0" ]; then
  cd /var/lib/urpmi
  rm -f compss provides depslist* descriptions.* *.cache hdlist.* synthesis.hdlist.* list.*
  cd /var/cache/urpmi
  rm -rf partial/* headers/* rpms/*
fi
exit 0

%triggerpostun -- urpmi < 6.18
# (mdvbz#45058#c10)
# fix packages wrongly marked installed-through-deps:
# ensure all rpmsrate pkgs are non orphans
# (the list of packages below is rpmsrate pkgs which are required by at least one pkg)
#
perl -Murpm::orphans -Murpm::util <<"EOF"
my @l = qw(RealPlayer WindowMaker abiword acpi acpid acroread alsa-utils aoss
apache-mod_perl apache-mod_php apache-mod_ssl apache-mod_suexec
apache-mpm-prefork ardour ark armagetron aspell-af aspell-am aspell-az
aspell-be aspell-bg aspell-bn aspell-br aspell-ca aspell-cs aspell-cy
aspell-da aspell-de aspell-el aspell-en aspell-eo aspell-es aspell-et
aspell-fa aspell-fi aspell-fo aspell-fr aspell-ga aspell-gd aspell-gl
aspell-gv aspell-he aspell-hi aspell-hr aspell-hsb aspell-hu aspell-id
aspell-is aspell-it aspell-ku aspell-lt aspell-lv aspell-mg aspell-mi
aspell-mk aspell-mn aspell-mr aspell-ms aspell-mt aspell-nds aspell-nl
aspell-nn aspell-no aspell-pa aspell-pl aspell-pt aspell-ro aspell-ru
aspell-rw aspell-sc aspell-sk aspell-sl aspell-sv aspell-sw aspell-ta
aspell-tl aspell-tr aspell-uk aspell-uz aspell-vi aspell-wa aspell-yi
aspell-zu at aumix autoconf automake awesfx bc beagle-evolution beagle-gui
bind bind-utils binutils bison bluez-gnome bluez-utils bootsplash brasero
busybox cdrkit cdrkit-genisoimage chromium claws-mail crack-attack
crack-attack-music crack-attack-sounds cvs dcraw desktop-common-data
dhcp-client dia dkms-zaptel dmidecode dosfstools drakconf efax eject ekiga
elisa emacs emacs-nox enscript eog epiphany epiphany-extensions evince
evolution extremetuxracer f-spot file file-roller firefox flex flphoto
fonts-ttf-arabic-arabeyes fonts-ttf-arabic-farsi fonts-ttf-arabic-kacst
fonts-ttf-chinese fonts-ttf-dejavu fonts-ttf-japanese fonts-ttf-korean
fonts-type1-greek fonts-type1-hebrew frozen-bubble gcalctool gcc gcc-c++
gconf-editor gdb gdm gedit gettext-devel ghostscript-module-X giftrans gimp
gnome-bluetooth gnome-games gnome-media gnome-system-monitor gnome-terminal
gnome-volume-manager gnupg gnuplot gphoto2 groff grub gsynaptics gthumb gtkam
gucharmap gurpmi hdparm hfsutils hylafax-client icewm icewm-light imagemagick
info inkscape inn iproute2 iptables iputils isdn4k-utils iwlwifi-4965-ucode
jabber java-1.6.0-openjdk-plugin java-1.6.0-sun java-1.6.0-sun-plugin jpilot
kaddressbook kcalc kcharselect kde4-l10n-ar kde4-l10n-be kde4-l10n-bg
kde4-l10n-ca kde4-l10n-cs kde4-l10n-csb kde4-l10n-da kde4-l10n-de kde4-l10n-el
kde4-l10n-en_GB kde4-l10n-eo kde4-l10n-es kde4-l10n-et kde4-l10n-eu
kde4-l10n-fa kde4-l10n-fi kde4-l10n-fr kde4-l10n-fy kde4-l10n-ga kde4-l10n-gl
kde4-l10n-hi kde4-l10n-hu kde4-l10n-is kde4-l10n-it kde4-l10n-ja kde4-l10n-kk
kde4-l10n-km kde4-l10n-ko kde4-l10n-ku kde4-l10n-lt kde4-l10n-lv kde4-l10n-mk
kde4-l10n-ml kde4-l10n-nb kde4-l10n-nds kde4-l10n-ne kde4-l10n-nl kde4-l10n-nn
kde4-l10n-pa kde4-l10n-pl kde4-l10n-pt kde4-l10n-pt_BR kde4-l10n-ro
kde4-l10n-ru kde4-l10n-se kde4-l10n-sl kde4-l10n-sr kde4-l10n-sv kde4-l10n-ta
kde4-l10n-th kde4-l10n-tr kde4-l10n-uk kde4-l10n-wa kde4-l10n-zh_CN
kde4-l10n-zh_TW kde4-nsplugins kdeaccessibility4 kdebluetooth4 kdenetwork-krfb
kdm kernel-server-latest kfloppy kino kipi-plugins kmail kmix knode knotes
kolab kompozer konsole kopete korganizer kppp krfb kscd ksnapshot ksynaptics
kterm laptop-mode-tools lbreakout2 lftp lib64alsa-plugins libtool lilo
linuxwacom lm_sensors lmms locales lsb lsb-core lsof lynx m4 mailman make man
man-pages mandriva-gfxboot-theme mandriva-release-Free mandriva-release-One
mandriva-release-Powerpack mandriva-theme-Free mandriva-theme-Free-screensaver
mandriva-theme-One mandriva-theme-One-screensaver mandriva-theme-Powerpack
mandriva-theme-Powerpack-screensaver mlocate monitor-edid mousepad
mozilla-thunderbird mtools myspell-af_ZA myspell-am_AM myspell-ar_AR
myspell-az_AZ myspell-bg_BG myspell-bn_BN myspell-ca_ES myspell-cop_EG
myspell-cs_CZ myspell-csb_CSB myspell-cy_GB myspell-da_DK myspell-de_AT
myspell-de_CH myspell-de_DE myspell-el_GR myspell-en_AU myspell-en_CA
myspell-en_GB myspell-en_NZ myspell-en_US myspell-en_ZA myspell-eo_EO
myspell-es_ES myspell-es_MX myspell-et_EE myspell-eu_ES myspell-fa_FA
myspell-fa_IR myspell-fj_FJ myspell-fo_FO myspell-fr_BE myspell-fr_FR
myspell-fur_IT myspell-fy_NL myspell-ga_IE myspell-gd_GB myspell-gl_ES
myspell-gsc_FR myspell-he_IL myspell-hi_IN myspell-hr_HR myspell-hu_HU
myspell-hy_AM myspell-id_ID myspell-is_IS myspell-it_IT myspell-km_KH
myspell-ku_TR myspell-la_LA myspell-lt_LT myspell-lv_LV myspell-mg_MG
myspell-mi_NZ myspell-mn_MN myspell-mr_IN myspell-ms_MY myspell-nb_NO
myspell-ne_NP myspell-nl_NL myspell-nn_NO myspell-nr_ZA myspell-ns_ZA
myspell-ny_MW myspell-oc_FR myspell-or_OR myspell-pa_PA myspell-pl_PL
myspell-pt_BR myspell-pt_PT myspell-qu_BO myspell-ro_RO myspell-ru_RU
myspell-rw_RW myspell-sk_SK myspell-sl_SI myspell-ss_ZA myspell-st_ZA
myspell-sv_SE myspell-sw_KE myspell-sw_TZ myspell-ta_TA myspell-tet_ID
myspell-th_TH myspell-tl_PH myspell-tn_ZA myspell-ts_ZA myspell-uk_UA
myspell-uz_UZ myspell-ve_ZA myspell-vi_VI myspell-xh_ZA myspell-zu_ZA
nautilus-cd-burner nautilus-filesharing ndiswrapper netprofile nfs-utils
nfs-utils-clients nmap nscd nspluginwrapper ntfs-3g ntfsprogs ntp nut-server
okular openldap-servers openoffice.org-calc openoffice.org-filter-binfilter
openoffice.org-impress openoffice.org-l10n-af openoffice.org-l10n-ar
openoffice.org-l10n-bg openoffice.org-l10n-br openoffice.org-l10n-bs
openoffice.org-l10n-ca openoffice.org-l10n-cs openoffice.org-l10n-cy
openoffice.org-l10n-da openoffice.org-l10n-de openoffice.org-l10n-el
openoffice.org-l10n-en_GB openoffice.org-l10n-es openoffice.org-l10n-et
openoffice.org-l10n-eu openoffice.org-l10n-fi openoffice.org-l10n-fr
openoffice.org-l10n-he openoffice.org-l10n-hi openoffice.org-l10n-hu
openoffice.org-l10n-it openoffice.org-l10n-ja openoffice.org-l10n-ko
openoffice.org-l10n-mk openoffice.org-l10n-nb openoffice.org-l10n-nl
openoffice.org-l10n-nn openoffice.org-l10n-pl openoffice.org-l10n-pt
openoffice.org-l10n-pt_BR openoffice.org-l10n-ru openoffice.org-l10n-sk
openoffice.org-l10n-sl openoffice.org-l10n-sv openoffice.org-l10n-ta
openoffice.org-l10n-tr openoffice.org-l10n-zh_CN openoffice.org-l10n-zh_TW
openoffice.org-l10n-zu openoffice.org-style-crystal openoffice.org-style-tango
openoffice.org-voikko openoffice.org-writer openoffice.org64-calc
openoffice.org64-filter-binfilter openoffice.org64-gnome
openoffice.org64-impress openoffice.org64-kde openoffice.org64-l10n-af
openoffice.org64-l10n-ar openoffice.org64-l10n-bg openoffice.org64-l10n-br
openoffice.org64-l10n-bs openoffice.org64-l10n-ca openoffice.org64-l10n-cs
openoffice.org64-l10n-cy openoffice.org64-l10n-da openoffice.org64-l10n-de
openoffice.org64-l10n-el openoffice.org64-l10n-en_GB openoffice.org64-l10n-es
openoffice.org64-l10n-et openoffice.org64-l10n-eu openoffice.org64-l10n-fi
openoffice.org64-l10n-fr openoffice.org64-l10n-he openoffice.org64-l10n-hi
openoffice.org64-l10n-hu openoffice.org64-l10n-it openoffice.org64-l10n-ja
openoffice.org64-l10n-ko openoffice.org64-l10n-mk openoffice.org64-l10n-nb
openoffice.org64-l10n-nl openoffice.org64-l10n-nn openoffice.org64-l10n-pl
openoffice.org64-l10n-pt openoffice.org64-l10n-pt_BR openoffice.org64-l10n-ru
openoffice.org64-l10n-sk openoffice.org64-l10n-sl openoffice.org64-l10n-sv
openoffice.org64-l10n-ta openoffice.org64-l10n-tr openoffice.org64-l10n-zh_CN
openoffice.org64-l10n-zh_TW openoffice.org64-l10n-zu
openoffice.org64-openclipart openoffice.org64-style-crystal
openoffice.org64-style-tango openoffice.org64-voikko openoffice.org64-writer
openssh-clients openssh-server patch pcmciautils perl perl-DBD-mysql
perl-Term-ReadLine-Gnu perl-devel perl-libwww-perl pidgin pinot planner
pm-utils postfix postgresql postgresql8.3-server ppp procmail proftpd psutils
python python-django qt4-doc quota rcs rhythmbox rox rp-pppoe rpm-build
rpmdrake rsync rxvt samba-client samba-server sane-frontends scim-anthy
scim-bridge scim-hangul scim-pinyin scim-tables-am scim-tables-zh screen
scribus sharutils smartmontools sound-scripts soundwrapper strace subversion
sudo supertux swatch synaptics taipeifonts task-gnome-minimal task-kde4
task-printing task-xfce-minimal tcpdump telnet-client-krb5 terminal
thunar-thumbnailers tkinter tmpwatch totem-gstreamer tpctl traceroute tvtime
uim-gtk unionfs-utils unzip urpmi urw-fonts userdrake valgrind vim-enhanced
vinagre vino voikko-fi webmin wget wireless-tools words wpa_supplicant
x11-driver-input x11-driver-video x11-font-bh-type1 xchat xchat-gnome
xfce4-mixer xfce4-taskmanager xfprint xine-ui xlockmore xorg-x11-75dpi-fonts
xsane xterm yp-tools ypbind ypserv zaptel-tools zip);

my $urpm = urpm->new;
my $unrequested = urpm::orphans::unrequested_list($urpm);

my @wrong = grep { delete $unrequested->{$_} } @l or exit;

my $file = urpm::orphans::unrequested_list__file($urpm);
print STDERR "removing from $file possibly required packages (cf mdvbz#45058): @wrong\n";
output_safe($file, 
	    join('', sort map { "$_\n" } keys %$unrequested),
	    ".old");
EOF
true

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
