#!/usr/bin/env bash
rsync -azvhP --no-t --stats --inplace --zc=zstd --ignore-existing --zl=3 output_songs/ ~/Nextcloud/20-29_Médias/20_Partitions/20.05_Real-Books-Individual-Songs/
rsync -azvhP --no-t --stats --inplace --zc=zstd --ignore-existing --zl=3 christmas/ ~/Nextcloud/20-29_Médias/20_Partitions/20.06_Christmas-Individual-Songs/
