%{?scl:%scl_package objectweb-asm3}
%{!?scl:%global pkg_name %{name}}

Name:           %{?scl_prefix}objectweb-asm3
Version:        3.3.1
Release:        14.2%{?dist}
Summary:        Java bytecode manipulation and analysis framework
License:        BSD
URL:            http://asm.ow2.org/
BuildArch:      noarch

Source0:        http://download.forge.ow2.org/asm/asm-%{version}.tar.gz
Source1:        http://www.apache.org/licenses/LICENSE-2.0.txt

BuildRequires:  %{?scl_prefix}ant
BuildRequires:  %{?scl_prefix}maven-local
# shade-jar utility used in this spec file needs this
BuildRequires:  %{?scl_prefix}objectweb-asm3

%description
ASM is an all purpose Java bytecode manipulation and analysis
framework.  It can be used to modify existing classes or dynamically
generate classes, directly in binary form.  Provided common
transformations and analysis algorithms allow to easily assemble
custom complex transformations and code analysis tools.

%package        javadoc
Summary:        API documentation for %{pkg_name}

%description    javadoc
This package provides %{summary}.

%prep
%setup -q -n asm-%{version}
find -name *.jar -delete

sed -i /Class-path/d archive/asm-xml.xml

# Our system version of asm always used BSN org.objectweb.asm for
# asm-all because that's what Eclipse bundle has.  Now upstream
# provides OSGi metadata with incompatible BSN, but we want to keep
# compatibility with existing Eclipse plugins, so we have to use the
# old BSN (org.objectweb.asm).
sed -i s/org.objectweb.asm.all/org.objectweb.asm/ archive/asm-all.xml

%build
%ant -Dobjectweb.ant.tasks.path= jar jdoc

mv output/dist/lib/all/* output/dist/lib/

# Fix artifactId in POMs for shaded artifacts
for m in asm asm-analysis asm-commons asm-tree asm-util asm-xml asm-all; do
    cp output/dist/lib/${m}-%{version}.pom output/dist/lib/${m}-distroshaded-%{version}.pom
    %pom_xpath_set "pom:project/pom:artifactId" "${m}-distroshaded" \
                   output/dist/lib/${m}-distroshaded-%{version}.pom
done

# Fix inter-module dependecies in POMs for shaded artifacts
%if 0%{?fedora} > 0
pushd output/dist/lib
for m in asm-analysis asm-commons asm-util; do
    %pom_remove_dep :asm-tree ${m}-distroshaded-%{version}.pom
    %pom_add_dep asm:asm-tree-distroshaded:3.3.1 ${m}-distroshaded-%{version}.pom
done
%pom_remove_dep :asm-util asm-xml-distroshaded-%{version}.pom
%pom_add_dep asm:asm-util-distroshaded:3.3.1 asm-xml-distroshaded-%{version}.pom

%pom_remove_dep :asm asm-tree-distroshaded-%{version}.pom
%pom_add_dep asm:asm-distroshaded:3.3.1 asm-tree-distroshaded-%{version}.pom
popd

for m in asm asm-analysis asm-commons asm-tree asm-util asm-xml asm-all; do
    shade-jar org.objectweb.asm org.objectweb.distroshaded.asm output/dist/lib/${m}-%{version}.jar \
              output/dist/lib/${m}-distroshaded-%{version}.jar
    jar xf output/dist/lib/${m}-distroshaded-%{version}.jar META-INF/MANIFEST.MF
    sed -i /Bundle-/d META-INF/MANIFEST.MF
    jar ufM output/dist/lib/${m}-distroshaded-%{version}.jar META-INF/MANIFEST.MF
done
%endif

%install
%mvn_artifact output/dist/lib/asm-parent-%{version}.pom

for m in asm asm-analysis asm-commons asm-tree asm-util asm-xml asm-all; do
%if 0%{?fedora} > 0
    %mvn_artifact output/dist/lib/${m}-distroshaded-%{version}.pom \
                  output/dist/lib/${m}-distroshaded-%{version}.jar
%endif
    %mvn_artifact output/dist/lib/${m}-%{version}.pom \
                  output/dist/lib/${m}-%{version}.jar
done
%mvn_install -J output/dist/doc/javadoc/user

%jpackage_script org.objectweb.asm.xml.Processor "" "" %{pkg_name}/asm:%{pkg_name}/asm-attrs:%{pkg_name}/asm-util:%{pkg_name}/asm-xml %{pkg_name}-processor true

%files -f .mfiles
%doc LICENSE.txt README.txt
%{_bindir}/%{pkg_name}-processor
%dir %{_javadir}/%{pkg_name}

%files javadoc -f .mfiles-javadoc
%doc LICENSE.txt

%changelog
* Thu Jun 22 2017 Michael Simacek <msimacek@redhat.com> - 3.3.1-14.2
- Mass rebuild 2017-06-22

* Wed Jun 21 2017 Java Maintainers <java-maint@redhat.com> - 3.3.1-14.1
- Automated package import and SCL-ization

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.3.1-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 3.3.1-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.1-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue Sep  2 2014 Darryl L. Pierce <dpierce@redhat.com> - 3.3.1-11
- First build for EPEL7.

* Fri Aug 29 2014 Darryl L. Pierce <dpierce@redhat.com> - 3.3.1-10.1
- Commented out BR on objectweb-asm3 to enable building on EPEL7.

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.1-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon Jan 20 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.3.1-9
- Remove Eclipse Orbit alias

* Mon Dec 16 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.3.1-8
- Remove OSGi metadata from shaded JARs
- Resolves: rhbz#1043066

* Fri Dec 06 2013 Michal Srb <msrb@redhat.com> - 3.3.1-7
- Separate artifacts for shaded asm

* Thu Dec 05 2013 Michal Srb <msrb@redhat.com> - 3.3.1-6
- Fix provides

* Thu Dec 05 2013 Michal Srb <msrb@redhat.com> - 3.3.1-5
- Build also "distroshaded" JARs and install them

* Thu Dec  5 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.3.1-4
- Change asm-all BSN to org.objectweb.asm

* Tue Dec  3 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.3.1-3
- Install asm-parent POM

* Thu Nov 14 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.3.1-2
- Remove classpath from manifest
- Install %{pkg_name}-processor command

* Mon Nov 11 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.3.1-1
- Initial packaging
