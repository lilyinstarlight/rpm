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

start_group 'Setup RPM environment'
set -x

rpmdev-setuptree

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

start_group 'Lint RPMs'
set -x

rpmlint -i "$HOME"/rpmbuild/SPECS/*.spec "$HOME"/rpmbuild/SRPMS/*.rpm "$HOME"/rpmbuild/RPMS/*/*.rpm

{ set +x; } 2>/dev/null
end_group
