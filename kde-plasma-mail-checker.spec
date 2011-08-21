Name: kde-plasma-mail-checker
Version: 1.1.12
Release: %(date +%Y%m%d_%H%M)%{?dist}
Summary: Plasmoid should periodic check for new messages in configured accounts.
Summary(ru): Плазмоид периодически проверяет наличие новых писем в списке почтовых ящиков.
#Group: Applications/Network
License: GPL
Source0: %{name}-%{version}.tar.bz2
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
URL: https://github.com/F1ash/plasmaMailChecker
BuildArch: noarch

%if %{defined fedora}
Requires: python >= 2.6, PyQt4 >= 4.7, PyKDE4 >= 4.6
Conflicts: python >= 3.0
BuildRequires: desktop-file-utils
%endif

%description
kde-plasma-mail-checker
Plasmoid should periodic check for new messages in configured accounts.
Supported protocols: POP3/POP3S/IMAP4/IMAP4S.
Passwords for accounts stored in encrypted container.
Plasmoid use KDE-notification for events about new mail.
Support Akonadi (mimeType : "message/rfc822") resources monitoring
(getting new mail).

%description -l ru
kde-plasma-mail-checker
Плазмоид периодически проверяет наличие новых писем
в списке почтовых ящиков.
Поддерживаются POP3\IMAP4 протоколы с None\SSL аутентификацией.
Пароли к почтовым ящикам содержатся в зашифрованном виде.
Плазмоид использует KDE-оповещение.
Плазмоид может отслеживать получение новой почты средствами Akonadi.

%prep
%setup -q

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{_kde4_appsdir}/plasma/plasmoids/%{name}
cp -r * $RPM_BUILD_ROOT/%{_kde4_appsdir}/plasma/plasmoids/%{name}/
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/kde4/services
cp -r metadata.desktop $RPM_BUILD_ROOT/%{_datadir}/kde4/services/%{name}.desktop


%files
%defattr(-,root,root)
%{_datadir}/kde4/services/%{name}.desktop
%{_kde4_appsdir}/plasma/plasmoids/%{name}/*
%dir %{_kde4_appsdir}/plasma/plasmoids/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%changelog

* Sun Aug 21 2011 Fl@sh <no@mail.me>	-	1.0
-- Build began ;)
