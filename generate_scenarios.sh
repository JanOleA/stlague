# Absolute limit of 4%
python election.py -t "Absolutt grense: 4% | Modifisert Sainte-Laguë" -f "./figs/abs4/modf" -l 4 -i 1.4 -a 1.8 -m stlague -PH
python election.py -t "Absolutt grense: 4% | Umodifisert Sainte-Laguë" -f "./figs/abs4/unmodf" -l 4 -i 1 -a 1.8 -m stlague -PH

# Varying area factors
python election.py -t "Ingen arealfaktor" -f "./figs/areal/faktor0" -l 4 -i 1.4 -a 0 -m stlague -P
python election.py -t "Arealfaktor 1 (normal er 1,8)" -f "./figs/areal/faktor1" -l 4 -i 1.4 -a 1 -m stlague -P
python election.py -t "Arealfaktor 3 (normal er 1,8)" -f "./figs/areal/faktor3" -l 4 -i 1.4 -a 3 -m stlague -P

# One nationwide electoral district
python election.py -t "Hele landet som ett valgdistrikt" -f "./figs/ett_distrikt" -l 0 -i 1.4 -a 1.8 -m stlague -PO

# No leveling seats
python election.py -t "Ingen utjevningsmandater | Modifisert Sainte-Laguë" -f "./figs/ingenutjvn/modf" -l 4 -i 1.4 -a 1.8 -m stlague -PN
python election.py -t "Ingen utjevningsmandater | Umodifisert Sainte-Laguë" -f "./figs/ingenutjvn/unmodf" -l 4 -i 1 -a 1.8 -m stlague -PN

# New counties
python election.py -t "Nye fylker som valgdistrikt | Modifisert Sainte-Laguë" -f "./figs/nyefylker/modf" -l 4 -i 1.4 -a 1.8 -m stlague -Pn
python election.py -t "Nye fylker som valgdistrikt | Umodifisert Sainte-Laguë" -f "./figs/nyefylker/unmodf" -l 4 -i 1 -a 1.8 -m stlague -Pn

# No leveling limit
python election.py -t "Ingen sperregrense | Modifisert Sainte-Laguë" -f "./figs/sperregrense0/modf" -l 0 -i 1.4 -a 1.8 -m stlague -P
python election.py -t "Ingen sperregrense | Umodifisert Sainte-Laguë" -f "./figs/sperregrense0/unmodf" -l 0 -i 1 -a 1.8 -m stlague -P

# 3% leveling limit
python election.py -t "Sperregrensen = 3% | Modifisert Sainte-Laguë" -f "./figs/sperregrense3/modf" -l 3 -i 1.4 -a 1.8 -m stlague -P
python election.py -t "Sperregrensen = 3% | Umodifisert Sainte-Laguë" -f "./figs/sperregrense3/unmodf" -l 3 -i 1 -a 1.8 -m stlague -P

# 4% leveling limit
python election.py -t "Sperregrensen = 4% | Modifisert Sainte-Laguë" -f "./figs/sperregrense4/modf" -l 4 -i 1.4 -a 1.8 -m stlague -P
python election.py -t "Sperregrensen = 4% | Umodifisert Sainte-Laguë" -f "./figs/sperregrense4/unmodf" -l 4 -i 1 -a 1.8 -m stlague -P

# 5% leveling limit
python election.py -t "Sperregrensen = 5% | Modifisert Sainte-Laguë" -f "./figs/sperregrense5/modf" -l 5 -i 1.4 -a 1.8 -m stlague -P
python election.py -t "Sperregrensen = 5% | Umodifisert Sainte-Laguë" -f "./figs/sperregrense5/unmodf" -l 5 -i 1 -a 1.8 -m stlague -P

# American ways (FPTP WTA)
python election.py -t "First Past The Post | norsk mandatfordeling" -f "./figs/usaway/stdmandater" -l 4 -i 1.4 -a 1.8 -m fptp -PN
python election.py -t "First Past The Post | amerikansk mandatfordeling" -f "./figs/usaway/usamandater" -l 4 -i 1 -a 1.8 -m fptp -PUN