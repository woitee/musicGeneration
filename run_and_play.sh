#!/bin/bash

while true; do
  py_out=$(python src/second_pcg.py)

  while read -r line; do
    local_seed=$(sed -ne 's/seed = \(.*\)/\1/p' <<< "$line")
    local_scale=$(sed -ne 's/scale = \(.*\)/\1/p' <<< "$line")
    local_start_note=$(sed -ne 's/start_note = \(.*\)/\1/p' <<< "$line")
    local_name=$(sed -ne 's/name = \(.*\)/\1/p' <<< "$line")
    seed=$seed || $local_seed
    if [[ -n "$local_seed" ]]; then
      seed=$local_seed
    fi
    if [[ -n "$local_scale" ]]; then
      scale=$(tr '_' ' ' <<< $local_scale)
    fi
    if [[ -n "$local_start_note" ]]; then
      start_note=$(sed -e 's/#/ sharp/' <<< $local_start_note)
    fi
    if [[ -n "$local_name" ]]; then
      name=$(tr '_' ' ' <<< $local_name)
    fi
  done <<<"$py_out"

  echo "seed is $seed"

  msg="Playing song titled $name. Which is in ${start_note:3} $scale"
  echo $msg
  say $msg

  open "out/$name.mid"
  sleep 18
done