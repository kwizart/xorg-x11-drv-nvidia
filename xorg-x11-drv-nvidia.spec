%global        _nvidia_serie        nvidia
%global        _nvidia_libdir       %{_libdir}/%{_nvidia_serie}
%global        _nvidia_xorgdir      %{_nvidia_libdir}/xorg
# Unfortunately this is always hardcoded regardless of architecture:
# https://github.com/NVIDIA/nvidia-installer/blob/master/misc.c#L2443
# https://github.com/NVIDIA/nvidia-installer/blob/master/misc.c#L2556-L2558
%global        _alternate_dir       %{_prefix}/lib/nvidia
%global        _glvnd_libdir        %{_libdir}/libglvnd

%if 0%{?rhel} == 6
%global        _modprobe_d          %{_sysconfdir}/modprobe.d/
# RHEL 6 does not have _udevrulesdir defined
%global        _udevrulesdir        %{_prefix}/lib/udev/rules.d/
%global        _modprobe_d          %{_sysconfdir}/modprobe.d/
%global        _dracutopts          nouveau.modeset=0 rdblacklist=nouveau
%global        _dracut_conf_d	    %{_sysconfdir}/dracut.conf.d
%global        _grubby              /sbin/grubby --grub --update-kernel=ALL
%else #rhel > 6 or fedora
%global        _dracut_conf_d	    %{_prefix}/lib/dracut.conf.d
%global        _modprobe_d          %{_prefix}/lib/modprobe.d/
%global        _grubby              %{_sbindir}/grubby --update-kernel=ALL
%if 0%{?rhel} == 7
%global        _dracutopts          nouveau.modeset=0 rd.driver.blacklist=nouveau
%else #fedora
%global        _dracutopts          rd.driver.blacklist=nouveau modprobe.blacklist=nouveau
%endif
%endif

%global	       debug_package %{nil}
%global	       __strip /bin/true


Name:            xorg-x11-drv-nvidia
Epoch:           2
Version:         375.66
Release:         8%{?dist}
Summary:         NVIDIA's proprietary display driver for NVIDIA graphic cards

License:         Redistributable, no modification permitted
URL:             http://www.nvidia.com/
Source0:         http://download.nvidia.com/XFree86/Linux-x86/%{version}/NVIDIA-Linux-x86-%{version}.run
Source1:         http://download.nvidia.com/XFree86/Linux-x86_64/%{version}/NVIDIA-Linux-x86_64-%{version}.run
Source2:         http://download.nvidia.com/XFree86/Linux-32bit-ARM/%{version}/NVIDIA-Linux-armv7l-gnueabihf-%{version}.run

Source3:         xorg.conf.nvidia
Source4:         99-nvidia.conf
Source5:         00-avoid-glamor.conf
Source6:         blacklist-nouveau.conf
Source7:         alternate-install-present
Source9:         nvidia-settings.desktop
Source10:        nvidia.conf
Source12:        xorg-x11-drv-nvidia.metainfo.xml
Source13:        parse-readme.py
Source14:        60-nvidia-uvm.rules
Source15:        nvidia-uvm.conf
Source16:        99-nvidia-dracut.conf

ExclusiveArch: i686 x86_64 armv7hl

BuildRequires:    desktop-file-utils
%if 0%{?rhel} > 6 || 0%{?fedora}
Buildrequires:    systemd
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd
%endif
%if 0%{?fedora} >= 25
# AppStream metadata generation
BuildRequires:    python2
BuildRequires:    libappstream-glib >= 0.6.3
# Xorg with PrimaryGPU
Requires:         Xorg >= 1.19.0-3
%else
# Xorg with OutputClass
Requires:         Xorg >= 1.16.0-1
%endif

Requires(post):   ldconfig
Requires(postun): ldconfig
Requires(post):   grubby
Requires:         which

Requires:        %{_nvidia_serie}-kmod >= %{?epoch}:%{version}
Requires:        %{name}-libs%{?_isa} = %{?epoch}:%{version}-%{release}

Obsoletes:       %{_nvidia_serie}-kmod < %{?epoch}:%{version}
Provides:        %{_nvidia_serie}-kmod-common = %{?epoch}:%{version}
Conflicts:       xorg-x11-drv-nvidia-304xx
Conflicts:       xorg-x11-drv-nvidia-340xx
Conflicts:       xorg-x11-drv-fglrx
Conflicts:       xorg-x11-drv-catalyst

%if 0%{?fedora} || 0%{?rhel} >= 7
%global         __provides_exclude ^(lib.*GL.*\\.so.*)$
%global         __requires_exclude ^(lib.*GL.*\\.so.*)$
%else

%{?filter_setup:
%filter_from_provides /^lib.*GL.*\.so/d;
%filter_from_requires /^lib.*GL.*\.so/d;
%filter_setup
}
%endif

%description
This package provides the most recent NVIDIA display driver which allows for
hardware accelerated rendering with current NVIDIA chipsets series.
GF8x, GF9x, and GT2xx GPUs NOT supported by this release.

For the full product support list, please consult the release notes
http://download.nvidia.com/XFree86/Linux-x86/%{version}/README/index.html

Please use the following documentation:
http://rpmfusion.org/Howto/nVidia


%package devel
Summary:         Development files for %{name}
Requires:        %{name}-libs%{?_isa} = %{?epoch}:%{version}-%{release}
Requires:        %{name}-cuda-libs%{?_isa} = %{?epoch}:%{version}-%{release}

#Don't put an epoch here
Provides:        cuda-drivers-devel = %{version}-100
Provides:        cuda-drivers-devel%{?_isa} = %{version}-100

%description devel
This package provides the development files of the %{name} package,
such as OpenGL headers.

%package cuda
Summary:         CUDA driver for %{name}
Requires:        %{_nvidia_serie}-kmod >= %{?epoch}:%{version}
Requires:        %{name}-cuda-libs%{?_isa} = %{?epoch}:%{version}-%{release}
Provides:        nvidia-persistenced = %{version}-%{release}
Requires:        ocl-icd%{?_isa}
Requires:        opencl-filesystem

Conflicts:       xorg-x11-drv-nvidia-340xx-cuda

#Don't put an epoch here
Provides:        cuda-drivers = %{version}-100
Provides:        cuda-drivers%{?_isa} = %{version}-100

%description cuda
This package provides the CUDA driver.

%package cuda-libs
Summary:         CUDA libraries for %{name}

%description cuda-libs
This package provides the CUDA driver libraries.

%package kmodsrc
Summary:         %{name} kernel module source code

%description kmodsrc
Source tree used for building kernel module packages (%{name}-kmod)
which is generated during the build of main package.

%package libs
Summary:         Libraries for %{name}
Requires:        libvdpau%{?_isa} >= 0.5
%if 0%{?fedora} >= 25
Requires:        libglvnd-egl%{?_isa} >= 0.2
Requires:        libglvnd-gles%{?_isa} >= 0.2
Requires:        libglvnd-glx%{?_isa} >= 0.2
Requires:        libglvnd-opengl%{?_isa} >= 0.2
Requires:        egl-wayland%{?_isa} >= 1.0.0
Requires:        mesa-libEGL%{?_isa} >= 13.0.3-3
Requires:        mesa-libGL%{?_isa} >= 13.0.3-3
Requires:        mesa-libGLES%{?_isa} >= 13.0.3-3
# Boolean dependencies are only fedora
%ifarch x86_64
Requires:        (%{name}-libs(x86-32) = %{?epoch}:%{version}-%{release} if libGL(x86-32))
%endif
%endif
%ifarch x86_64 i686
Requires:        vulkan-filesystem
%endif

%description libs
This package provides the shared libraries for %{name}.


%prep
%setup -q -c -T
#Only extract the needed arch
%ifarch %{ix86}
sh %{SOURCE0} \
%endif
%ifarch x86_64
sh %{SOURCE1} \
%endif
%ifarch armv7hl
sh %{SOURCE2} \
%endif
  --extract-only --target nvidiapkg-%{_target_cpu}
ln -s nvidiapkg-%{_target_cpu} nvidiapkg


%build
# Nothing to build
echo "Nothing to build"


%install
cd nvidiapkg

# Install only required libraries
mkdir -p %{buildroot}%{_libdir}
cp -a \
    libcuda.so.%{version} \
    libEGL_nvidia.so.%{version} \
    libGLESv1_CM_nvidia.so.%{version} \
    libGLESv2_nvidia.so.%{version} \
    libGLX_nvidia.so.%{version} \
    libnvcuvid.so.%{version} \
    libnvidia-cfg.so.%{version} \
    libnvidia-eglcore.so.%{version} \
    libnvidia-encode.so.%{version} \
    libnvidia-fatbinaryloader.so.%{version} \
    libnvidia-fbc.so.%{version} \
    libnvidia-glcore.so.%{version} \
    libnvidia-glsi.so.%{version} \
    libnvidia-gtk*.so.%{version} \
    libnvidia-ifr.so.%{version} \
    libnvidia-ml.so.%{version} \
    libnvidia-ptxjitcompiler.so.%{version} \
    %{buildroot}%{_libdir}/

# Use the correct TLS implementation for x86_64/i686, already ok on ARM
# OpenCL is only available on x86_64/i686.
%ifarch x86_64 i686
cp -af \
    tls/libnvidia-tls.so* \
    libnvidia-compiler.so.%{version} \
    libnvidia-opencl.so.%{version} \
    %{buildroot}%{_libdir}/
%else
cp -af libnvidia-tls.so* %{buildroot}%{_libdir}/
%endif

# Use ldconfig for libraries with a mismatching SONAME/filename
ldconfig -vn %{buildroot}%{_libdir}/

# Libraries you can link against
for lib in libcuda libnvcuvid libnvidia-encode; do
    ln -sf $lib.so.%{version} %{buildroot}%{_libdir}/$lib.so
done

# Vdpau driver
install -D -p -m 0755 libvdpau_nvidia.so.%{version} %{buildroot}%{_libdir}/vdpau/libvdpau_nvidia.so.%{version}
ln -sf libvdpau_nvidia.so.%{version} %{buildroot}%{_libdir}/vdpau/libvdpau_nvidia.so.1

# GlVND
%if 0%{?fedora} >= 25
# We keep the same symlink than mesa-libGL to avoid conflict
ln -s %{_libdir}/libGLX_mesa.so.0 %{buildroot}%{_libdir}/libGLX_indirect.so.0
%else
ln -s libGLX_nvidia.so.%{version} %{buildroot}%{_libdir}/libGLX_indirect.so.0
# ld.so.conf.d file
install -m 0755 -d       %{buildroot}%{_sysconfdir}/ld.so.conf.d/
echo -e "%{_nvidia_libdir} \n" > %{buildroot}%{_sysconfdir}/ld.so.conf.d/nvidia-%{_lib}.conf
%endif

# X DDX driver and GLX extension
install -p -D -m 0755 libglx.so.%{version} %{buildroot}%{_nvidia_xorgdir}/libglx.so.%{version}
ln -sf libglx.so.%{version} %{buildroot}%{_nvidia_xorgdir}/libglx.so
install -D -p -m 0755 nvidia_drv.so %{buildroot}%{_libdir}/xorg/modules/drivers/nvidia_drv.so

%ifarch x86_64 i686
# OpenCL config
install    -m 0755         -d %{buildroot}%{_sysconfdir}/OpenCL/vendors/
install -p -m 0644 nvidia.icd %{buildroot}%{_sysconfdir}/OpenCL/vendors/
# Vulkan config
install    -m 0755         -d %{buildroot}%{_datadir}/vulkan/icd.d/
install -p -m 0644 nvidia_icd.json %{buildroot}%{_datadir}/vulkan/icd.d/
%endif

# EGL config for libglvnd
install    -m 0755         -d %{buildroot}%{_datadir}/glvnd/egl_vendor.d/
install -p -m 0644 10_nvidia.json %{buildroot}%{_datadir}/glvnd/egl_vendor.d/10_nvidia.json

# Blacklist nouveau, autoload nvidia-uvm module after nvidia module
mkdir -p %{buildroot}%{_modprobe_d}
install -p -m 0644 %{SOURCE15} %{buildroot}%{_modprobe_d}
%if ! 0%{?fedora} >= 25
install -p -m 0644 %{SOURCE6} %{buildroot}%{_modprobe_d}
%endif

# UDev rules for nvidia-uvm
install    -m 0755 -d          %{buildroot}%{_udevrulesdir}
install -p -m 0644 %{SOURCE14} %{buildroot}%{_udevrulesdir}

# dracut.conf.d file, nvidia modules must never be in the initrd
install -p -m 0755 -d          %{buildroot}%{_dracut_conf_d}/
install -p -m 0644 %{SOURCE16} %{buildroot}%{_dracut_conf_d}/

# Install binaries
install -m 0755 -d %{buildroot}%{_bindir}
install -p -m 0755 nvidia-{bug-report.sh,debugdump,smi,cuda-mps-control,cuda-mps-server,xconfig,settings,persistenced} \
  %{buildroot}%{_bindir}

# Install headers
install -m 0755 -d %{buildroot}%{_includedir}/nvidia/GL/
install -p -m 0644 {gl.h,glext.h,glx.h,glxext.h} %{buildroot}%{_includedir}/nvidia/GL/

# Install man pages
install    -m 0755 -d   %{buildroot}%{_mandir}/man1/
install -p -m 0644 nvidia-{cuda-mps-control,persistenced,settings,smi,xconfig}.1.gz \
  %{buildroot}%{_mandir}/man1/

# Install nvidia icon
mkdir -p %{buildroot}%{_datadir}/pixmaps
install -pm 0644 nvidia-settings.png %{buildroot}%{_datadir}/pixmaps

# Fix desktop file and validate
sed -i -e 's|__UTILS_PATH__/||g' -e 's|__PIXMAP_PATH__/||g' nvidia-settings.desktop
sed -i -e 's|nvidia-settings.png|nvidia-settings|g' nvidia-settings.desktop
desktop-file-install --vendor "" \
    --dir %{buildroot}%{_datadir}/applications/ \
    nvidia-settings.desktop

#Alternate-install-present is checked by the nvidia .run
mkdir -p %{buildroot}%{_alternate_dir}
install -p -m 0644 %{SOURCE7} %{buildroot}%{_alternate_dir}

#install the NVIDIA supplied application profiles
mkdir -p %{buildroot}%{_datadir}/nvidia
install -p -m 0644 nvidia-application-profiles-%{version}-{rc,key-documentation} %{buildroot}%{_datadir}/nvidia

#Install the Xorg configuration files
mkdir -p %{buildroot}%{_sysconfdir}/X11/xorg.conf.d
mkdir -p %{buildroot}%{_datadir}/X11/xorg.conf.d
%if 0%{?fedora} >= 25
install -pm 0644 %{SOURCE10} %{buildroot}%{_datadir}/X11/xorg.conf.d/nvidia.conf
sed -i -e 's|@LIBDIR@|%{_libdir}|g' %{buildroot}%{_datadir}/X11/xorg.conf.d/nvidia.conf
touch -r %{SOURCE10} %{buildroot}%{_datadir}/X11/xorg.conf.d/nvidia.conf
%else
install -pm 0644 nvidia-drm-outputclass.conf %{buildroot}%{_datadir}/X11/xorg.conf.d/nvidia.conf
install -pm 0644 %{SOURCE4} %{buildroot}%{_datadir}/X11/xorg.conf.d
sed -i -e 's|@LIBDIR@|%{_libdir}|g' %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/99-nvidia.conf
touch -r %{SOURCE4} %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/99-nvidia.conf
%endif
#Ghost Xorg nvidia.conf files
touch %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/00-avoid-glamor.conf
touch %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/99-nvidia.conf
touch %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/nvidia.conf

#Install the initscript
tar jxf nvidia-persistenced-init.tar.bz2
%if 0%{?rhel} > 6 || 0%{?fedora}
mkdir -p %{buildroot}%{_unitdir}
install -pm 0644 nvidia-persistenced-init/systemd/nvidia-persistenced.service.template \
  %{buildroot}%{_unitdir}/nvidia-persistenced.service
#Change the daemon running owner
sed -i -e "s/__USER__/root/" %{buildroot}%{_unitdir}/nvidia-persistenced.service
%endif

#Create the default nvidia config directory
mkdir -p %{buildroot}%{_sysconfdir}/nvidia

#Install the nvidia kernel modules sources archive
mkdir -p %{buildroot}%{_datadir}/nvidia-kmod-%{version}
tar Jcf %{buildroot}%{_datadir}/nvidia-kmod-%{version}/nvidia-kmod-%{version}-%{_target_cpu}.tar.xz kernel

#Add autostart file for nvidia-settings to load user config
install -D -p -m 0644 %{SOURCE9} %{buildroot}%{_sysconfdir}/xdg/autostart/nvidia-settings.desktop

%if 0%{?fedora} >= 25
# install AppData and add modalias provides
mkdir -p %{buildroot}%{_datadir}/appdata/
install -pm 0644 %{SOURCE12} %{buildroot}%{_datadir}/appdata/
fn=%{buildroot}%{_datadir}/appdata/xorg-x11-drv-nvidia.metainfo.xml
%{SOURCE13} README.txt "NVIDIA GEFORCE GPUS" | xargs appstream-util add-provide ${fn} modalias
%{SOURCE13} README.txt "NVIDIA QUADRO GPUS" | xargs appstream-util add-provide ${fn} modalias
%{SOURCE13} README.txt "NVIDIA NVS GPUS" | xargs appstream-util add-provide ${fn} modalias
%{SOURCE13} README.txt "NVIDIA TESLA GPUS" | xargs appstream-util add-provide ${fn} modalias
%endif


%pre
if [ "$1" -eq "1" ]; then
  if [ -x %{_bindir}/nvidia-uninstall ]; then
    %{_bindir}/nvidia-uninstall -s && rm -f %{_bindir}/nvidia-uninstall &>/dev/null || :
  fi
fi

%post
/sbin/ldconfig
if [ "$1" -eq "1" ]; then
  %{_grubby} --args='%{_dracutopts}' &>/dev/null
%if 0%{?fedora} || 0%{?rhel} >= 7
  sed -i -e 's/GRUB_CMDLINE_LINUX="/GRUB_CMDLINE_LINUX="%{_dracutopts} /g' /etc/default/grub
%endif
fi || :

%if 0%{?fedora} || 0%{?rhel} >= 7
%triggerun -- xorg-x11-drv-nvidia < 2:375.66-7
if [ -f %{_sysconfdir}/default/grub ] ; then
  sed -i -e '/GRUB_GFXPAYLOAD_LINUX=text/d' %{_sysconfdir}/default/grub
  . %{_sysconfdir}/default/grub
  if [ -z "${GRUB_CMDLINE_LINUX+x}" ]; then
    echo -e GRUB_CMDLINE_LINUX=\"%{_dracutopts}\" >> %{_sysconfdir}/default/grub
  else
    for i in %{_dracutopts} ; do
      _has_string=$(echo ${GRUB_CMDLINE_LINUX} | fgrep -c $i)
      if [ x"$_has_string" = x0 ] ; then
        GRUB_CMDLINE_LINUX="${GRUB_CMDLINE_LINUX} ${i}"
      fi
    done
    sed -i -e "s|^GRUB_CMDLINE_LINUX=.*|GRUB_CMDLINE_LINUX=\"${GRUB_CMDLINE_LINUX}\"|g" %{_sysconfdir}/default/grub
  fi
fi
%{_grubby} --args='%{_dracutopts}' &>/dev/null || :
%endif

%post libs -p /sbin/ldconfig

%post cuda
%if 0%{?rhel} > 6 || 0%{?fedora}
%systemd_post nvidia-persistenced.service
%endif

%post cuda-libs -p /sbin/ldconfig

%if 0%{?rhel} == 6
%posttrans
[ -f %{_sysconfdir}/X11/xorg.conf ] || cp -p %{_sysconfdir}/X11/xorg.conf.nvidia %{_sysconfdir}/X11/xorg.conf || :
%endif

%preun
if [ "$1" -eq "0" ]; then
  %{_grubby} --remove-args='%{_dracutopts}' &>/dev/null
%if 0%{?fedora} || 0%{?rhel} >= 7
  sed -i -e 's/%{_dracutopts} //g' /etc/default/grub
%endif
  # Backup and disable previously used xorg.conf
  [ -f %{_sysconfdir}/X11/xorg.conf ] && mv %{_sysconfdir}/X11/xorg.conf %{_sysconfdir}/X11/xorg.conf.nvidia_uninstalled &>/dev/null
fi ||:

%if 0%{?rhel} > 6 || 0%{?fedora}
%preun cuda
%systemd_preun nvidia-persistenced.service
%endif

%postun -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%postun cuda
%if 0%{?rhel} > 6 || 0%{?fedora}
%systemd_postun_with_restart nvidia-persistenced.service
%endif

%postun cuda-libs -p /sbin/ldconfig

%files
%license nvidiapkg/LICENSE
%doc nvidiapkg/NVIDIA_Changelog
%doc nvidiapkg/README.txt
%doc nvidiapkg/nvidia-application-profiles-%{version}-rc
%doc nvidiapkg/html
%dir %{_alternate_dir}
%{_alternate_dir}/alternate-install-present
%ifarch x86_64 i686
%{_datadir}/vulkan/icd.d/nvidia_icd.json
%endif
%{_datadir}/glvnd/egl_vendor.d/10_nvidia.json
%dir %{_sysconfdir}/nvidia
%ghost %{_sysconfdir}/X11/xorg.conf.d/00-avoid-glamor.conf
%ghost %{_sysconfdir}/X11/xorg.conf.d/99-nvidia.conf
%ghost %{_sysconfdir}/X11/xorg.conf.d/nvidia.conf
%if 0%{?fedora} >= 25
%{_datadir}/appdata/xorg-x11-drv-nvidia.metainfo.xml
%{_dracut_conf_d}/99-nvidia-dracut.conf
%{_datadir}/X11/xorg.conf.d/nvidia.conf
%else
# Owns the directory since libglvnd is optional here
%dir %{_datadir}/glvnd
%dir %{_datadir}/glvnd/egl_vendor.d
%{_datadir}/X11/xorg.conf.d/00-avoid-glamor.conf
%{_datadir}/X11/xorg.conf.d/99-nvidia.conf
# RHEL6 uses /etc
%if 0%{?rhel} == 6
%config(noreplace) %{_modprobe_d}/blacklist-nouveau.conf
%config(noreplace) %{_dracut_conf_d}/99-nvidia-dracut.conf
%else
%{_modprobe_d}/blacklist-nouveau.conf
%{_dracut_conf_d}/99-nvidia-dracut.conf
%endif
%endif
%config %{_sysconfdir}/xdg/autostart/nvidia-settings.desktop
%{_bindir}/nvidia-bug-report.sh
%{_bindir}/nvidia-settings
%{_bindir}/nvidia-xconfig
# Xorg libs that do not need to be multilib
%dir %{_nvidia_xorgdir}
%{_nvidia_xorgdir}/libglx.so
%{_nvidia_xorgdir}/libglx.so.%{version}
%{_libdir}/xorg/modules/drivers/nvidia_drv.so
%ifarch %{arm}
%{_libdir}/libnvidia-gtk2.so.%{version}
%endif
%ifarch x86_64 i686
%if 0%{?rhel} == 6
%exclude %{_libdir}/libnvidia-gtk3.so.%{version}
%{_libdir}/libnvidia-gtk2.so.%{version}
%else
%exclude %{_libdir}/libnvidia-gtk2.so.%{version}
%{_libdir}/libnvidia-gtk3.so.%{version}
%endif
%endif
#/no_multilib
%dir %{_datadir}/nvidia
%{_datadir}/nvidia/nvidia-application-profiles-%{version}-*
%{_datadir}/applications/*nvidia-settings.desktop
%{_datadir}/pixmaps/*.png
%{_mandir}/man1/nvidia-settings.*
%{_mandir}/man1/nvidia-xconfig.*

%files kmodsrc
%dir %{_datadir}/nvidia-kmod-%{version}
%{_datadir}/nvidia-kmod-%{version}/nvidia-kmod-%{version}-%{_target_cpu}.tar.xz

%files libs
%if 0%{?rhel} || 0%{?fedora} == 24
%config %{_sysconfdir}/ld.so.conf.d/nvidia-%{_lib}.conf
%endif
%dir %{_nvidia_libdir}
%{_libdir}/libEGL_nvidia.so.0
%{_libdir}/libEGL_nvidia.so.%{version}
%{_libdir}/libGLESv1_CM_nvidia.so.1
%{_libdir}/libGLESv1_CM_nvidia.so.%{version}
%{_libdir}/libGLESv2_nvidia.so.2
%{_libdir}/libGLESv2_nvidia.so.%{version}
%{_libdir}/libGLX_indirect.so.0
%{_libdir}/libGLX_nvidia.so.0
%{_libdir}/libGLX_nvidia.so.%{version}
%{_libdir}/libnvidia-cfg.so.1
%{_libdir}/libnvidia-cfg.so.%{version}
%{_libdir}/libnvidia-eglcore.so.%{version}
%{_libdir}/libnvidia-fbc.so.1
%{_libdir}/libnvidia-fbc.so.%{version}
%{_libdir}/libnvidia-glcore.so.%{version}
%{_libdir}/libnvidia-glsi.so.%{version}
%{_libdir}/libnvidia-ifr.so.1
%{_libdir}/libnvidia-ifr.so.%{version}
%{_libdir}/libnvidia-tls.so.%{version}
%{_libdir}/vdpau/libvdpau_nvidia.so.1
%{_libdir}/vdpau/libvdpau_nvidia.so.%{version}

%files cuda
%license nvidiapkg/LICENSE
%if 0%{?rhel} > 6 || 0%{?fedora}
%{_unitdir}/nvidia-persistenced.service
%endif
%{_bindir}/nvidia-debugdump
%{_bindir}/nvidia-smi
%{_bindir}/nvidia-cuda-mps-control
%{_bindir}/nvidia-cuda-mps-server
%{_bindir}/nvidia-persistenced
%ifarch x86_64 i686
%config %{_sysconfdir}/OpenCL/vendors/nvidia.icd
%endif
%{_mandir}/man1/nvidia-smi.*
%{_mandir}/man1/nvidia-cuda-mps-control.1.*
%{_mandir}/man1/nvidia-persistenced.1.*
%{_modprobe_d}/nvidia-uvm.conf
%{_udevrulesdir}/60-nvidia-uvm.rules

%files cuda-libs
%{_libdir}/libcuda.so
%{_libdir}/libcuda.so.1
%{_libdir}/libcuda.so.%{version}
%{_libdir}/libnvcuvid.so.1
%{_libdir}/libnvcuvid.so.%{version}
%{_libdir}/libnvidia-encode.so.1
%{_libdir}/libnvidia-encode.so.%{version}
%{_libdir}/libnvidia-fatbinaryloader.so.%{version}
%{_libdir}/libnvidia-ml.so.1
%{_libdir}/libnvidia-ml.so.%{version}
%{_libdir}/libnvidia-ptxjitcompiler.so.%{version}
%ifarch x86_64 i686
%{_libdir}/libnvidia-compiler.so.%{version}
%{_libdir}/libnvidia-opencl.so.1
%{_libdir}/libnvidia-opencl.so.%{version}
%endif

%files devel
%{_includedir}/nvidia/
%{_libdir}/libnvcuvid.so
%{_libdir}/libnvidia-encode.so

%changelog
* Wed Jul 05 2017 Nicolas Chauvet <kwizart@gmail.com> - 2:375.66-8
- Make libglvnd optional on rhel
- Use boolean dependency on fedora 25 also

* Tue Jun 13 2017 Nicolas Chauvet <kwizart@gmail.com> - 2:375.66-7
- Use | instead of / for sed GRUB_CMDLINE_LINUX

* Fri Jun 02 2017 Nicolas Chauvet <kwizart@gmail.com> - 2:375.66-6
- Remove GRUB_GFXPAYLOAD_LINUX from default/grub

* Tue May 30 2017 Nicolas Chauvet <kwizart@gmail.com> - 2:375.66-5
- Update the triggerin to insert the new cmdline
- Avoid the nvidia modules to get added to the initramfs - patch by hansg

* Tue May 30 2017 Leigh Scott <leigh123linux@googlemail.com> - 2:375.66-3
- Revert 10_nvidia.json rename

* Fri May 12 2017 Nicolas Chauvet <kwizart@gmail.com> - 2:375.66-2
- Add epoch for triggerin

* Fri May 05 2017 Leigh Scott <leigh123linux@googlemail.com> - 2:375.66-1
- Update to 375.66 release

* Wed Apr 26 2017 Nicolas Chauvet <kwizart@gmail.com> - 1:381.09-5
- Use modprobe.blacklist cmdline instead of blacklist file on fedora.
- Use triggerin to install the new cmdline
- Re-org Xorg config files installation
- Switch to http instead of ftp for download URL
- Point libGLX_indirect to Mesa on f25+ or to nvidia

* Mon Apr 10 2017 Simone Caronni <negativo17@gmail.com> - 1:381.09-3
- Also use split libglvnd packages for Fedora 24 and RHEL 6/7.

* Mon Apr 10 2017 Simone Caronni <negativo17@gmail.com> - 1:381.09-2
- Simplify GRUB installation for Grub 1 (RHEL 6) and Grub 2 (RHEL 7+/Fedora), do
  not use obsolete kernel parameters.
- Add kernel parameters to default grub file on Fedora/RHEL 7+.
- Bring default RHEL 6 X.org configuration on par with Fedora/RHEL 7+ and make
  sure it is installed by default.
- Install RHEL 6 X.org configuration template only on RHEL 6, make sure it does
  not end in .conf to avoid confusion.
- Package only required symlinks for libraries.
- Add only the libraries that program can link to in the devel subpackage.
- Make CUDA subpackages multilib compliant (no more CUDA i686 binaries on
  x86_64).
- Do not require main packages for libraries subpackages, this makes possible to
  build things that link to Nvidia drivers using only libraries and not pulling
  all the graphic driver components.
- Fix files listed twice during build.
- Install non conflicting libraries in standard locations, remove all redundant
  directory overrides for the various distributions. This also removes the link
  libGLX_indirect.so.0.
- Explicitly list all libraries included in the packages, avoid too many
  if/exclude directives.
- Various fixups from Nicolas Chauvet:
  * buildroot
  * glvnd vulkan to use _datadir
  * Use nvidia_libdir for alternate install file
  * arm and opencl

* Fri Apr 07 2017 Leigh Scott <leigh123linux@googlemail.com> - 1:381.09-1
- Update to 381.09 beta

* Tue Mar 14 2017 Leigh Scott <leigh123linux@googlemail.com> - 1:378.13-2
- Link libGLX_indirect.so.0 to libGLX_mesa.so.0

* Fri Mar 03 2017 Leigh Scott <leigh123linux@googlemail.com> - 1:378.13-1
- Update to 378.13 release

* Thu Mar 02 2017 Simone Caronni <negativo17@gmail.com> - 1:375.39-7
- Use gtk 2 nvidia-settings library only on RHEL 6 and Fedora ARM.

* Thu Mar 02 2017 Simone Caronni <negativo17@gmail.com> - 1:375.39-6
- Require source built libnvidia-egl-wayland library.

* Thu Mar 02 2017 Simone Caronni <negativo17@gmail.com> - 1:375.39-5
- Use only newer ELF TLS implementation, supported since kernel 2.3.99 (pre RHEL
  4).

* Thu Mar 02 2017 Simone Caronni <negativo17@gmail.com> - 1:375.39-4
- Remove OpenCL loader, RPM filters and ownership of loader configuration.
- Require OpenCL filesystem and loader library.

* Thu Mar 02 2017 Simone Caronni <negativo17@gmail.com> - 1:375.39-3
- Replace SUID nvidia-modprobe binary with configuration. Make sure the
  nvidia-uvm module is loaded when the CUDA subpackage is installed and that
  dracut does not try to pull in the module in the initrd.
- Remove leftovers from old distributions.
- Remove prelink configuration.
- Make sure the license is installed both with the base driver package and with
  the CUDA package.
- Make sure the package also builds and install on RHEL 6.
- Enable SLI and BaseMosaic by default on Fedora 25+.
- Trim changelog (<2015).

* Thu Feb 16 2017 Nicolas Chauvet <kwizart@gmail.com> - 1:375.39-2
- Avoid xorg dir symlink on fedora 25+
- Drop GFXPAYLOAD and video=vesa:off
- Implement cuda-libs (for steam)

* Tue Feb 14 2017 Leigh Scott <leigh123linux@googlemail.com> - 1:375.39-1
- Update to 375.39 release

* Thu Jan 19 2017 Leigh Scott <leigh123linux@googlemail.com> - 1:375.26-11
- Fix file conflict with filesystem

* Wed Jan 18 2017 Leigh Scott <leigh123linux@googlemail.com> - 1:375.26-10
- Add conditions for el7 as there is no wayland

* Wed Jan 18 2017 Leigh Scott <leigh123linux@googlemail.com> - 1:375.26-9
- Add conditions for f24 and el7

* Tue Jan 17 2017 Leigh Scott <leigh123linux@googlemail.com> - 1:375.26-8
- Changes for mesa glvnd
- Move nvidia libs to lib directoy and remove ldconfig config file
- Add appdata info

* Sat Dec 31 2016 leigh scott <leigh123linux@googlemail.com> - 1:375.26-7
- Update nvidia.conf for latest Xorg changes

* Sat Dec 24 2016 leigh scott <leigh123linux@googlemail.com> - 1:375.26-6
- Fix error in nvidia.conf rfbz#4388

* Sat Dec 24 2016 leigh scott <leigh123linux@googlemail.com> - 1:375.26-5
- Add xorg-x11-server-Xorg minimum version requires

* Mon Dec 19 2016 leigh scott <leigh123linux@googlemail.com> - 1:375.26-4
- Add conditionals for f24

* Mon Dec 19 2016 leigh scott <leigh123linux@googlemail.com> - 1:375.26-3
- Fix nvidia.conf

* Sun Dec 18 2016 leigh scott <leigh123linux@googlemail.com> - 1:375.26-2
- Change conf files for Prime support

* Wed Dec 14 2016 leigh scott <leigh123linux@googlemail.com> - 1:375.26-1
- Update to 375.26 release

* Fri Nov 18 2016 leigh scott <leigh123linux@googlemail.com> - 1:375.20-1
- Update to 375.20 release

* Mon Oct 24 2016 Leigh Scott <leigh123linux@googlemail.com> - 1:375.10-2
- Add glvnd/egl_vendor.d file
- Add requires vulkan-filesystem

* Fri Oct 21 2016 Leigh Scott <leigh123linux@googlemail.com> - 1:375.10-1
- Update to 375.10 beta release
- Clean up more libglvnd provided libs

* Wed Oct 12 2016 Leigh Scott <leigh123linux@googlemail.com> - 1:370.28-5
- Add libglvnd path to ld.so.conf.d conf file

* Tue Oct 11 2016 Leigh Scott <leigh123linux@googlemail.com> - 1:370.28-4
- Switch to system libglvnd
- Fix unowned file links

* Fri Sep 30 2016 Leigh Scott <leigh123linux@googlemail.com> - 1:370.28-3
- add xorg abi override

* Tue Sep 13 2016 Leigh Scott <leigh123linux@googlemail.com> - 1:370.28-2
- readd libGLdispatch.so.0

* Fri Sep 09 2016 Leigh Scott <leigh123linux@googlemail.com> - 1:370.28-1
- Update to 370.28
- Remove surplus glvnd libs (not used)
- Prepare for fedora glvnd package

* Fri Aug 19 2016 Leigh Scott <leigh123linux@googlemail.com> - 1:370.23-1
- Update to 370.23 beta

* Wed Aug 10 2016 Leigh Scott <leigh123linux@googlemail.com> - 1:367.35-3
- Revert last commit
- add ldconfig in %%post and %%postun for main package rfbz#3998

* Wed Aug 10 2016 Leigh Scott <leigh123linux@googlemail.com> - 1:367.35-2
- Move setttings libs to libs sub-package rfbz#3998

* Sun Jul 17 2016 Leigh Scott <leigh123linux@googlemail.com> - 1:367.35-1
- Update to 367.35

* Sat Jul 16 2016 Leigh Scott <leigh123linux@googlemail.com> - 1:367.27-2
- Add vulkan icd profile

* Fri Jul 01 2016 Leigh Scott <leigh123linux@googlemail.com> - 1:367.27-1
- Update to 367.27

* Wed Jun 22 2016 Nicolas Chauvet <kwizart@gmail.com> - 1:367.27-1
- Update to 367.27

* Wed Jan 27 2016 Nicolas Chauvet <kwizart@gmail.com> - 1:358.16-2
- Enforce GRUB_GFXPAYLOAD_LINUX=text even for EFI - prevent this message:
  The NVIDIA Linux graphics driver requires the use of a text-mode VGA console
  Use of other console drivers including, but not limited to, vesafb, may
  result in corruption and stability problems, and is not supported.
  To verify , check cat /proc/driver/nvidia/./warnings/fbdev

* Sat Nov 21 2015 Nicolas Chauvet <kwizart@gmail.com> - 1:358.16-1
- Update to 358.16
- Remove posttrans for fedora < 21
- Remove ignoreabi config file as it rarely works

* Mon Aug 31 2015 Leigh Scott <leigh123linux@googlemail.com> - 1:355.11-1
- Update to 355.11

* Fri Aug 28 2015 Leigh Scott <leigh123linux@googlemail.com> - 1:352.41-1
- Update to 352.41

* Tue Jul 28 2015 Leigh Scott <leigh123linux@googlemail.com> - 1:352.30-1
- Update to 352.30

* Mon Jun 15 2015 Leigh Scott <leigh123linux@googlemail.com> - 1:352.21-1
- Update to 352.21

* Wed May 20 2015 Leigh Scott <leigh123linux@googlemail.com> - 1:346.72-1
- Update to 343.72

* Wed Apr 08 2015 Leigh Scott <leigh123linux@googlemail.com> - 1:346.59-1
- Update to 343.59

* Tue Feb 24 2015 Leigh Scott <leigh123linux@googlemail.com> - 1:346.47-1
- Update to 343.47

* Sun Feb 15 2015 Nicolas Chauvet <kwizart@gmail.com> - 1:346.35-4
- Fix build for armhfp

* Mon Jan 26 2015 Nicolas Chauvet <kwizart@gmail.com> - 1:346.35-3
- Add cuda-driver-devel and %%{_isa} virtual provides

* Wed Jan 21 2015 Leigh Scott <leigh123linux@googlemail.com> - 1:346.35-2
- clean up gtk from libs sub-package

* Fri Jan 16 2015 Leigh Scott <leigh123linux@googlemail.com> - 1:346.35-1
- Update to 346.35

* Sun Jan 11 2015 Nicolas Chauvet <kwizart@gmail.com> - 1:343.36-2
- Move libnvidia-ml back into -cuda along with nvidia-debugdump
