Name: kde-plasma-mail-checker
Version: 1.15.63
Release: 2%{?dist}
Summary: KDE Plasmoid for periodically checking a new messages in the mailboxes list
Summary(ru): Плазмоид периодически проверяет наличие новых писем в списке почтовых ящиков
License: GPLv2+
Source0: https://github.com/F1ash/%{name}/archive/%{version}.tar.gz
URL: https://github.com/F1ash/%{name}
BuildArch: noarch

Requires: python-SocksiPy, python-mailer
BuildRequires: kdelibs4-devel
# for building the translator`s dictionary
BuildRequires: qt4-devel

%description
%{name}
Plasmoid periodically checking for new messages in configured accounts.
Supported protocols: POP3/POP3S/IMAP4/IMAP4S + IMAP4_IDLE.
Passwords for accounts stored in encrypted container.
Plasmoid use KDE-notification for events about new mail.
Support Akonadi (mimeType : "message/rfc822") resources monitoring
(getting new mail).
Support preview (integrated mail viewer) for non-Akonadi accounts
and Quick Answer & Forward Mail.

%description -l ru
%{name}
Плазмоид периодически проверяет наличие новых писем
в списке почтовых ящиков.
Поддерживаются POP3\IMAP4(+IDLE) протоколы с None\SSL аутентификацией.
Пароли к почтовым ящикам содержатся в зашифрованном виде.
Плазмоид использует KDE-оповещение.
Плазмоид может отслеживать получение новой почты средствами Akonadi.
Есть встроенный предпросмотр почты для обычных аккаунтов
с возможностью быстрого ответа и пересылки.

%prep
%setup -q

%build
if [ -x %{_bindir}/plasma-dataengine-depextractor ] ; then
  plasma-dataengine-depextractor .
fi
make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT/usr

%files
%{_kde4_datadir}/kde4/services/%{name}.desktop
%{_kde4_appsdir}/plasma/plasmoids/%{name}
%doc README README_RU COPYING Changelog Licenses

%changelog
* Wed Aug 14 2013 Fl@sh <kaperang07@gmail.com> - 1.15.63-2
- description improved;

* Fri Jul 26 2013 Fl@sh <kaperang07@gmail.com> - 1.15.63-1
- version update;

* Mon Jun 10 2013 Fl@sh <kaperang07@gmail.com> - 1.15.62-1
- version update;

* Fri May 24 2013 Fl@sh <kaperang07@gmail.com> - 1.15.60-1
- version update;

* Tue May 21 2013 Fl@sh <kaperang07@gmail.com> - 1.14.60-1
- version update;

* Tue May 14 2013 Fl@sh <kaperang07@gmail.com> - 1.13.59-1
- version update;

* Sun May 12 2013 Fl@sh <kaperang07@gmail.com> - 1.12.58-1
- version update;

* Sun Apr 28 2013 Fl@sh <kaperang07@gmail.com> - 1.12.56-1
- version update;
- clear spec`s changelog;
