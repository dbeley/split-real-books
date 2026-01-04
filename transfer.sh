#!/usr/bin/env bash
rsync -azvhP --stats --no-t --inplace --zc=zstd --update --delete-after --zl=3 --checksum output_songs/ ~/Nextcloud/40-49_Médias/41_Partitions/41.15_Real-Books-Individual-Songs/
rsync -azvhP --stats --no-t --inplace --zc=zstd --update --delete-after --zl=3 --checksum christmas/ ~/Nextcloud/40-49_Médias/41_Partitions/41.16_Christmas-Individual-Songs/
rsync -azvhP --stats --no-t --inplace --zc=zstd --update --delete-after --zl=3 --checksum output_songs_combined.pdf ~/Nextcloud/40-49_Médias/41_Partitions/
