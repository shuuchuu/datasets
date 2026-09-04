#!/usr/bin/env bash
# ghsparse.sh — télécharge un seul dossier du dépôt github.com/shuuchuu/datasets,
# via partial clone (--filter=blob:none) + sparse checkout : seuls les fichiers
# du dossier ciblé sont rapatriés.
#
#   usage : ghsparse.sh <dossier> [destination] [branche]
#   ex.   : ghsparse.sh images
#           ghsparse.sh data/images /content/images dev
#
#   depuis Colab : !wget -qO- https://github.com/shuuchuu/datasets/raw/refs/heads/main/ghsparse.sh | bash -s landscape

set -euo pipefail

REPO=shuuchuu/datasets

[ $# -ge 1 ] || { echo "usage: $(basename "$0") <dossier> [destination] [branche]" >&2; exit 1; }

folder=${1#/}; folder=${folder%/}
dest=${2:-$(basename "$folder")}
branch=${3:-}

[ -n "$folder" ] || { echo "erreur : dossier vide" >&2; exit 1; }
[ ! -e "$dest" ] || { echo "erreur : '$dest' existe déjà" >&2; exit 1; }

mkdir -p "$(dirname "$dest")"
# clone temporaire à côté de la destination : le mv final est alors un simple
# renommage, instantané même avec 300 000 fichiers
work=$(mktemp -d "$(dirname "$dest")/.ghsparse.XXXXXX")
trap 'rm -rf "$work"' EXIT

opts=(--filter=blob:none --sparse --depth 1)
[ -z "$branch" ] || opts+=(--branch "$branch")

git clone -q "${opts[@]}" "https://github.com/$REPO.git" "$work"
git -C "$work" sparse-checkout set --cone "$folder"

[ -d "$work/$folder" ] || { echo "erreur : '$folder' introuvable dans $REPO${branch:+ (branche $branch)}" >&2; exit 1; }
mv "$work/$folder" "$dest"

echo "✓ $dest — $(find "$dest" -type f | wc -l) fichiers, $(du -sh "$dest" | cut -f1)"
