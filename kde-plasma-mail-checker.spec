Name: kde-plasma-mail-checker
Version: 1.1.12
Release: 1%{?dist}
Summary: KDE Plasmoid for periodically checking a new messages in the mailboxes list.
Summary(ru): Плазмоид периодически проверяет наличие новых писем в списке почтовых ящиков.
Group: Applications/Network
License: GPL
Source0: http://cloud.github.com/downloads/F1ash/plasmaMailChecker/%{name}-%{version}.tar.bz2
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
URL: https://github.com/F1ash/plasmaMailChecker
BuildArch: noarch

Requires: python, PyQt4, PyKDE4
BuildRequires: qt-devel

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

%build
make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT/usr

%files
%defattr(-,root,root)
%{_datadir}/kde4/services/%{name}.desktop
%{_datadir}/kde4/apps/plasma/plasmoids/%{name}/*
%dir %{_datadir}/kde4/apps/plasma/plasmoids/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%changelog

* Mon Aug 22 2011 Fl@sh <kaperang07@gmail.com> - 1.1.12-1
- Initial build
