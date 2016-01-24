#!/bin/bash

D=testexample1_template
OD=testexample1

mkdir -p $OD

for FN in $D/members.json \
	      $D/members_meta.json \
	      $D/*_founding_vote.json \
	      $D/buip1.txt \
	      $D/buip1_meta.json \
	      $D/*_buip1_vote.json \
	      $D/buip1_election.json \
	      $D/newmembers.json \
	      $D/newmembers_meta.json \
	      $D/*_newmembers_vote.json; do
    ./buv fill-template $FN $OD${FN#$D}
done
	      
cp $D/filelist.json $OD

	      
