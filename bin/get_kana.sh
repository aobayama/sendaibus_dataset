#!/bin/sh

# get yomigana data from www.navi.kotsu.city.sendai.jp

# set GNU sed
sed=gsed
outdir=../csv
outcsv=${outdir}/yomigana.csv

# initialize
[ ! -d $outdir ] && mkdir -p $outdir
[ -f $outcsv ] && rm -f $outcsv
touch $outcsv

for shiin in x k s t n h m r y w
do
    for boin in a i u e o
    do

        [ "$shiin" = "s" ] && [ "$boin" = "o" ] && continue
        [ "$shiin" = "r" ] && [ "$boin" = "u" ] && continue
        [ "$shiin" = "y" ] && [ "$boin" = "i" ] && continue
        [ "$shiin" = "y" ] && [ "$boin" = "e" ] && continue
        [ "$shiin" = "w" ] && [ ! "$boin" = "a" ] && continue
        [ "$shiin" = "x" ] && shiin=""

        echo "processing: $shiin$boin"

        uri="http://www.navi.kotsu.city.sendai.jp/dia/route/web/exp.cgi?val_htmb=start&val_method=3&val_kana=${shiin}${boin}&val_search_type=1"
        echo $uri

        dat=`curl -s $uri | nkf -Lu -w8 | grep gojuon_detail2 | $sed -e 's/^.*self">//g' | $sed -e 's/<.*$//g' | $sed -e 's/／バス/,/g' | $sed -e 's/$/%%N%%/g' | $sed -e 's/,%%N%%/,/g' | tr -d '\n' | $sed 's/%%N%%/\n/g'`

        cat << EOF >> $outcsv
$dat
EOF

        echo "wrote: $shiin$boin"

        sleep 1

    done
done

