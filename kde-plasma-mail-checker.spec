Name: kde-plasma-mail-checker
Version: 1.7.39
Release: 1%{?dist}
Summary: KDE Plasmoid for periodically checking a new messages in the mailboxes list
Summary(ru): Плазмоид периодически проверяет наличие новых писем в списке почтовых ящиков
Group: Applications/Internet
License: GPLv2+
Source0: http://cloud.github.com/downloads/F1ash/plasmaMailChecker/%{name}-%{version}.tar.bz2
URL: https://github.com/F1ash/plasmaMailChecker
BuildArch: noarch

Requires: PyKDE4, python-SocksiPy
BuildRequires: kde-filesystem
# for building the translator`s dictionary
BuildRequires: qt4-devel

%description
kde-plasma-mail-checker
Plasmoid should periodic check for new messages in configured accounts.
Supported protocols: POP3/POP3S/IMAP4/IMAP4S + IMAP4_IDLE.
Passwords for accounts stored in encrypted container.
Plasmoid use KDE-notification for events about new mail.
Support Akonadi (mimeType : "message/rfc822") resources monitoring
(getting new mail).

%description -l ru
kde-plasma-mail-checker
Плазмоид периодически проверяет наличие новых писем
в списке почтовых ящиков.
Поддерживаются POP3\IMAP4(+IDLE) протоколы с None\SSL аутентификацией.
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
%{_kde4_datadir}/kde4/services/%{name}.desktop
%{_kde4_appsdir}/plasma/plasmoids/%{name}
%doc README README_RU COPYING

%changelog
* Wed Sep 5 2012 Fl@sh <kaperang07@gmail.com> - 1.7.39-1
- version updated

* Tue Sep 4 2012 Fl@sh <kaperang07@gmail.com> - 1.7.38-1
- version updated

* Sat Aug 18 2012 Fl@sh <kaperang07@gmail.com> - 1.7.37-1
- version updated

* Thu Aug 2 2012 Fl@sh <kaperang07@gmail.com> - 1.7.36-1
- version updated

* Mon Jul 23 2012 Fl@sh <kaperang07@gmail.com> - 1.7.35-2
- fixed build requires

* Mon Jul 23 2012 Fl@sh <kaperang07@gmail.com> - 1.7.35-1
- added kde-settings build require
- fixed file path
- version updated

* Fri Jul 20 2012 Fl@sh <kaperang07@gmail.com> - 1.7.34-1
- version updated

* Thu Jul 19 2012 Fl@sh <kaperang07@gmail.com> - 1.7.31-1
- improved files path
- version updated

* Mon Jul 16 2012 Fl@sh <kaperang07@gmail.com> - 1.7.30-1
- version updated

* Fri Jul 13 2012 Fl@sh <kaperang07@gmail.com> - 1.6.28-1
- version updated

* Wed Jul 11 2012 Fl@sh <kaperang07@gmail.com> - 1.6.27-1
- improved description
- version updated

* Sun Jun 24 2012 Fl@sh <kaperang07@gmail.com> - 1.5.25-1
- version updated

* Sat Mar 10 2012 Fl@sh <kaperang07@gmail.com> - 1.5.22-1
- version updated

* Sat Mar 10 2012 Fl@sh <kaperang07@gmail.com> - 1.5.21-1
- version updated

* Sun Feb 15 2012 Fl@sh <kaperang07@gmail.com> - 1.5.20-14.R
- added python-SocksiPy require;
- version updated

* Sun Feb 10 2012 Fl@sh <kaperang07@gmail.com> - 1.4.20-13.R
- version updated

* Sun Feb  6 2012 Fl@sh <kaperang07@gmail.com> - 1.4.19-12.R
- version updated

* Sun Feb  5 2012 Fl@sh <kaperang07@gmail.com> - 1.4.18-11.R
- version updated

* Thu Dec 30 2011 Fl@sh <kaperang07@gmail.com> - 1.3.18-10.R
- version updated

* Thu Dec 29 2011 Fl@sh <kaperang07@gmail.com> - 1.2.17-9.R
- version updated

* Sun Dec 18 2011 Fl@sh <kaperang07@gmail.com> - 1.2.15-8.R
- version updated

* Sat Dec 17 2011 Fl@sh <kaperang07@gmail.com> - 1.2.14-8.R
- version updated

* Tue Oct 11 2011 Fl@sh <kaperang07@gmail.com> - 1.1.14-7
- some fixes

* Mon Oct 10 2011 Fl@sh <kaperang07@gmail.com> - 1.1.13-7
- some fixes

* Thu Sep 1 2011 Fl@sh <kaperang07@gmail.com> - 1.1.12-7
- fixed Group

* Tue Aug 30 2011 Fl@sh <kaperang07@gmail.com> - 1.1.12-6
- fixed Makefile

* Tue Aug 30 2011 Fl@sh <kaperang07@gmail.com> - 1.1.12-5
- fixed Makefile

* Tue Aug 30 2011 Fl@sh <kaperang07@gmail.com> - 1.1.12-4
- added get source script

* Mon Aug 29 2011 Fl@sh <kaperang07@gmail.com> - 1.1.12-3
- fixed Makefile

* Mon Aug 29 2011 Fl@sh <kaperang07@gmail.com> - 1.1.12-2
- fixed Makefile

* Mon Aug 22 2011 Fl@sh <kaperang07@gmail.com> - 1.1.12-1
- Initial build
