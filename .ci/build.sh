#!/bin/bash -e
start_group() {
  if [ "$GITHUB_ACTIONS" == "true" ]; then
    # shellcheck disable=SC2016
    echo "::group::$(echo -e "$*" | sed -e '1h;2,$H;$!d;g' -e 's/%/%25/g' -e 's/\r/%0D/g' -e 's/\n/%0A/g')" >&2
  fi
}

end_group() {
  if [ "$GITHUB_ACTIONS" == "true" ]; then
    echo "::endgroup::" >&2
  fi
}

start_group 'Packaging metadata'
set -x

pretty="Fooster"
name="$(echo "$pretty" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')"
base="https://file.lily.flowers/rpm"
signer="Lily Foster (rpm) <lily@lily.flowers>"

{ set +x; } 2>/dev/null
end_group

start_group 'Import GPG private key'
set -x

export GNUPGHOME="$(mktemp -d)"
printenv GPG_KEY | base64 -d | gpg --import

{ set +x; } 2>/dev/null
end_group

start_group 'Setup RPM environment'
set -x

rpmdev-setuptree
echo "%_gpg_name $signer" >>"$HOME"/.rpmmacros

{ set +x; } 2>/dev/null
end_group

start_group 'Copy RPM specs'
set -x

find . -type f -name '*.spec' -exec cp '{}' "$HOME"/rpmbuild/SPECS/ ';'

{ set +x; } 2>/dev/null
end_group

for spec in "$HOME"/rpmbuild/SPECS/*.spec; do
	start_group "Build $(basename "$spec")"
	set -x

	dnf builddep -y "$spec"
	spectool -g -R "$spec"
	rpmbuild -ba "$spec"

	{ set +x; } 2>/dev/null
	end_group
done

start_group 'Sign RPMs'

for rpm in "$HOME"/rpmbuild/SRPMS/*.rpm "$HOME"/rpmbuild/RPMS/*/*.rpm; do
	set -x

	rpm --addsign "$rpm"

	{ set +x; } 2>/dev/null
done

end_group

start_group 'Create src repo'
set -x

mkdir -p "$HOME"/www

cp -r "$HOME"/rpmbuild/SRPMS "$HOME"/www/src
createrepo "$HOME"/www/src
gpg -u "$signer" --detach-sign --armor "$HOME"/www/src/repodata/repomd.xml

{ set +x; } 2>/dev/null
end_group

for archdir in "$HOME"/rpmbuild/RPMS/*; do
	arch="$(basename "$archdir")"

	start_group "Create $arch repo"
	set -x

	cp -r "$HOME"/rpmbuild/RPMS/"$arch" "$HOME"/www/"$arch"
	createrepo "$HOME"/www/"$arch"
	gpg -u "$signer" --detach-sign --armor "$HOME"/www/"$arch"/repodata/repomd.xml

	{ set +x; } 2>/dev/null
	end_group
done

start_group 'Export GPG public key'
set -x

gpg --export -a "$signer" >"$HOME"/www/key.asc

{ set +x; } 2>/dev/null
end_group

start_group "Create yum repo files"

echo "+ cat >'$HOME/www/$name-src.repo'" >&2
cat >"$HOME"/www/"$name"-src.repo <<EOF
[$name-src]
name=$pretty - Source
baseurl=$base/src/
gpgcheck=1
enabled=1
gpgkey=$base/key.asc
EOF

echo "+ cat >'$HOME/www/$name.repo'" >&2
cat >"$HOME"/www/"$name".repo <<EOF
[$name]
name=$pretty
baseurl=$base/\$basearch/
gpgcheck=1
enabled=1
gpgkey=$base/key.asc
EOF

end_group
