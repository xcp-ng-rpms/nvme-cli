%global package_speccommit 84661f59302d8737f7f06bcd2bd95359d8721b68
%global usver 1.16
%global xsver 6
%global xsrel %{xsver}%{?xscount}%{?xshash}

#%%global commit0 bdbb4da0979fbdc079cf98410cdb31cf799e83b3
#%%global shortcommit0 %%(c=%%{commit0}; echo ${c:0:7})

Name:           nvme-cli
Version:        1.16
Release:        %{?xsrel}%{?dist}
Summary:        NVMe management command line interface

License:        GPLv2+
URL:            https://github.com/linux-nvme/nvme-cli
Source0: v1.16.tar.gz
Patch0: nvme-cli-makefile-dont-install-host-params-patch
Patch1: 0001-fabrics-fix-nvme-connect-segfault-if-transport-type-.patch
Patch2: 0002-fabrics-fix-a-buffer-overrun.patch
Patch3: 0003-bash-Fix-nvme-completion.patch
Patch4: 0004-nvme-do-not-leak-an-open-file-handle.patch
Patch5: 0005-nvme-topology-fix-memory-leaks-in-nvme_logical_block.patch
Patch6: 0006-nvme-cli-nvmf-connect-.service-Remove-matching-from-.patch
Patch7: 0007-nvme-cli-Make-connect-all-matching-be-case-insensiti.patch
Patch8: 0008-nvme-cli-nvme-gen-hostnqn-use-partition-UUID-on-IBM-.patch
Patch9: 0009-Add-new-events-support-in-PEL.patch
Patch10: 0010-nvme-cli-Decode-Supported-Events-Bitmap-in-PEL-heade.patch
Patch11: 0011-nvme-cli-Adds-event-number-in-persistent-event-entri.patch
Patch12: 0012-nvme-cli-Adds-readable-firmware-level-in-persistent.patch
Patch13: 0013-nvme-cli-Add-support-set-feature-event-in-PEL.patch
Patch14: 0014-nvme-cli-Add-support-Telemetry-CRT-in-PEL.patch
Patch15: 0015-fix-firmware-log-page-frs-variable-sign.patch
Patch16: 0016-fix-file-permissions-nvme-print.c.patch


BuildRequires:  libuuid-devel
BuildRequires:  gcc
BuildRequires:  systemd-devel
Requires:       util-linux

%description
nvme-cli provides NVM-Express user space tooling for Linux.

%prep
#%%setup -qn %%{name}-%%{commit0}
%autosetup -p1

%build

# CFLAGS on the command line breaks the build.  It works okay as an
# environment variable, though.  See:
# https://github.com/linux-nvme/nvme-cli/pull/480
CFLAGS="%{optflags}" make PREFIX=/usr LDFLAGS="%{__global_ldflags}" %{?_smp_mflags}


%install
%make_install PREFIX=/usr UDEVDIR="%{_udevrulesdir}/.." SYSTEMDDIR="%{_unitdir}/.."
mkdir -p %{buildroot}%{_sysconfdir}/nvme

# hostid and hostnqn are supposed to be unique per machine.  We obviously
# can't package them.
#rm -f %{buildroot}%{_sysconfdir}/nvme/hostid
#rm -f %{buildroot}%{_sysconfdir}/nvme/hostnqn

# Do not install the dracut rule yet.  See rhbz 1742764
rm -f %{buildroot}/usr/lib/dracut/dracut.conf.d/70-nvmf-autoconnect.conf


%files
%license LICENSE
%doc README.md
%{_sbindir}/nvme
%{_mandir}/man1/nvme*.gz
%{_datadir}/bash-completion/completions/nvme
%{_datadir}/zsh/site-functions/_nvme
%dir %{_sysconfdir}/nvme
%{_unitdir}/nvmefc-boot-connections.service
%{_unitdir}/nvmf-autoconnect.service
%{_unitdir}/nvmf-connect.target
%{_unitdir}/nvmf-connect@.service
%{_udevrulesdir}/70-nvmf-autoconnect.rules
%{_udevrulesdir}/71-nvmf-iopolicy-netapp.rules
# Do not install the dracut rule yet.  See rhbz 1742764
# /usr/lib/dracut/dracut.conf.d/70-nvmf-autoconnect.conf

%post
if [ $1 -eq 1 ] || [ $1 -eq 2 ]; then
        if [ ! -s %{_sysconfdir}/nvme/hostnqn ]; then
		echo $(nvme gen-hostnqn) > %{_sysconfdir}/nvme/hostnqn
        fi
        if [ ! -s %{_sysconfdir}/nvme/hostid ]; then
                uuidgen > %{_sysconfdir}/nvme/hostid
        fi

	# apply udev and systemd changes that we did
	systemctl enable nvmefc-boot-connections
	systemctl daemon-reload
	udevadm control --reload-rules && udevadm trigger
	exit 0
fi

%changelog
* Thu Oct 13 2022 Maurizio Lombardi <mlombard@redhat.com> - 1.16-6
- Fix a file permission

* Fri Jul 15 2022 Maurizio Lombardi <mlombard@redhat.com> - 1.16-5
- Fix a compiler warning

* Tue Jul 12 2022 Maurizio Lombardi <mlombard@redhat.com> - 1.16-4
- Merge fixes for PowerPC

* Fri Jan 07 2022 Maurizio Lombardi <mlombard@redhat.com> - 1.16-3
- Merge a few bugfixes

* Mon Nov 29 2021 Maurizio Lombardi <mlombard@redhat.com> - 1.16-2
- Update to version 1.16

* Thu Jul 22 2021 Maurizio Lombardi <mlombard@redhat.com> - 1.14-2
- Merge various bugfixes

* Wed Apr 28 2021 Maurizio Lombardi <mlombard@redhat.com> - 1.14-1
- Update to version v1.14

* Tue Apr 20 2021 Maurizio Lombardi <mlombard@redhat.com> - 1.13-4
- Rebuild to mark bz1949462 as fixed

* Fri Apr 16 2021 Maurizio Lombardi <mlombard@redhat.com> - 1.13-3
- KATO values fixes for various controllers

* Wed Apr 14 2021 Maurizio Lombardi <mlombard@redhat.com> - 1.13-2
- Add dependency to util-linux and fix the post install script

* Wed Apr 14 2021 Maurizio Lombardi <mlombard@redhat.com> - 1.13-1
- Update to 1.13

* Tue Jun 16 2020 Fedora Release Monitoring <release-monitoring@fedoraproject.org> - 1.12-1
- Update to 1.12 (#1827581)

* Sat Apr 25 2020 luto@kernel.org - 1.11.1-1
- Update to 1.11

* Thu Mar 19 2020 luto@kernel.org - 1.10.1-1
- Update to 1.10.1

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Wed Oct 02 2019 luto@kernel.org - 1.9-1
- Update to 1.9
- Certain fabric functionality may not work yet due to missing dracut
  support and missing hostid and hostnqn configuration.

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.8.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Mon Apr 15 2019 luto@kernel.org - 1.8.1-1
- Update to 1.8.1-1.
- Remove a build hack.

* Sun Feb 24 2019 luto@kernel.org - 1.7-2
- Create /etc/nvme

* Sun Feb 24 2019 luto@kernel.org - 1.7-1
- Bump to 1.7
- Clean up some trivial rpmlint complaints

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Tue Jul 24 2018 luto@kernel.org - 1.6-1
- Update to 1.6

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.4-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Nov 22 2017 luto@kernel.org - 1.4-1
- Update to 1.4

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon May 22 2017 luto@kernel.org - 1.3-1
- Update to 1.3

* Wed Apr 19 2017 luto@kernel.org - 1.2-2
- Update to 1.2
- 1.2-1 never existed

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Feb 01 2017 luto@kernel.org - 1.1-1
- Update to 1.1

* Sun Nov 20 2016 luto@kernel.org - 1.0-1
- Update to 1.0

* Mon Oct 31 2016 luto@kernel.org - 0.9-1
- Update to 0.9

* Thu Jun 30 2016 luto@kernel.org - 0.8-1
- Update to 0.8

* Tue May 31 2016 luto@kernel.org - 0.7-1
- Update to 0.7

* Fri Mar 18 2016 luto@kernel.org - 0.5-1
- Update to 0.5

* Sun Mar 06 2016 luto@kernel.org - 0.4-1
- Update to 0.4

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.2-3.20160112gitbdbb4da
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jan 20 2016 luto@kernel.org - 0.2-2.20160112gitbdbb4da
- Update to new upstream commit, fixing #49.  "nvme list" now works.

* Wed Jan 13 2016 luto@kernel.org - 0.2-1.20160112gitde3e0f1
- Initial import.
