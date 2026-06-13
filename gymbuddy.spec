Name:           gymbuddy
Version:        0.1.0
Release:        1%{?dist}
Summary:        Workout tracker with Obsidian vault integration

License:        MIT
URL:            https://github.com/conner/gymbuddy
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
BuildRequires:  python3-rpm-macros

Requires:       python3 >= 3.11
Requires:       python3-PyQt6 >= 6.6
Requires:       python3-PyYAML >= 6.0
Requires:       python3-dateutil >= 2.9
Requires:       python3-openai >= 1.30

%description
GymBuddy is a desktop application for logging workouts with direct
Obsidian vault markdown integration. Features include:

* Daily workout logging (exercises, sets, reps, weight, RPE)
* Goal tracking with target dates
* Split-based exercise presets (Push/Pull/Legs/Upper/Lower/Full Body)
* Exercise library management
* Progress charts and analytics
* AI Coach integration (OpenAI/Ollama compatible)
* Catppuccin Mocha dark theme
* Configurable units (metric/imperial)

%prep
%autosetup -n workout-tracker-%{version}

%build
%py3_build

%install
%py3_install

# Install desktop file
mkdir -p %{buildroot}%{_datadir}/applications
install -m 644 assets/gymbuddy.desktop %{buildroot}%{_datadir}/applications/gymbuddy.desktop

# Install icon
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
install -m 644 assets/gymbuddy.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/gymbuddy.svg

# Install entry point script
mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/gymbuddy << 'EOF'
#!/bin/sh
# GymBuddy entry point for system installation
mkdir -p "$HOME/.config/workout-tracker"
exec python3 -m workout_tracker.main "$@"
EOF
chmod 755 %{buildroot}%{_bindir}/gymbuddy

%files
%license LICENSE
%doc README.md
%{python3_sitelib}/workout_tracker/
%{python3_sitelib}/workout_tracker-*.egg-info/
%{_bindir}/gymbuddy
%{_datadir}/applications/gymbuddy.desktop
%{_datadir}/icons/hicolor/scalable/apps/gymbuddy.svg

%changelog
* Thu Jun 13 2026 Conner <conner@example.com> - 0.1.0-1
- Initial release of GymBuddy workout tracker