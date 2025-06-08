#!/usr/bin/env bash
rsync -azvhP --stats --no-t --inplace --zc=zstd --update --delete-after --zl=3 output_songs/ ~/Nextcloud/20-29_Médias/20_Partitions/20.05_Real-Books-Individual-Songs/
rsync -azvhP --stats --no-t --inplace --zc=zstd --update --delete-after --zl=3 christmas/ ~/Nextcloud/20-29_Médias/20_Partitions/20.06_Christmas-Individual-Songs/
