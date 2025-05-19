#!/bin/bash

src="$1"
if [ -z "$src" ]
then
    echo "Usage: $0 <svgcal.svg>"
    exit 1
else
    sed -i -e "s/Jan/Январь/;s/Feb/Февраль/;s/Mar/Март/;s/Apr/Апрель/;s/May/Май/;s/Jun/Июль/;s/Jul/Июль/;s/Aug/Август/;s/Sep/Сентябрь/;s/Oct/Октябрь/;s/Nov/Ноябрь/;s/Dec/Декабрь/;s/Mn/Пн/g;s/Tu/Вт/g;s/Wd/Ср/g;s/Th/Чт/g;s/Fr/Пт/g;s/St/Сб/g;s/Sn/Вс/g;" "$src"
fi
