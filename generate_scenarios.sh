echo "Absolute limit of 4%"
python election.py -t "Absolutt grense: 4% | Modifisert Sainte-Laguë" -f "./figs/abs4/modf" -l 4 -i 1.4 -a 1.8 -m stlague -PHS
python election.py -t "Absolutt grense: 4% | Umodifisert Sainte-Laguë" -f "./figs/abs4/unmodf" -l 4 -i 1 -a 1.8 -m stlague -PHS

echo ""
echo "Varying area factors"
python election.py -t "Ingen arealfaktor" -f "./figs/areal/faktor0" -l 4 -i 1.4 -a 0 -m stlague -PS
python election.py -t "Arealfaktor 1 (normal er 1,8)" -f "./figs/areal/faktor1" -l 4 -i 1.4 -a 1 -m stlague -PS
python election.py -t "Arealfaktor 3 (normal er 1,8)" -f "./figs/areal/faktor3" -l 4 -i 1.4 -a 3 -m stlague -PS

echo ""
echo "One nationwide electoral district"
python election.py -t "Hele landet som ett valgdistrikt" -f "./figs/ett_distrikt" -l 0 -i 1.4 -a 1.8 -m stlague -POS

echo ""
echo "No leveling seats"
python election.py -t "Ingen utjevningsmandater | Modifisert Sainte-Laguë" -f "./figs/ingenutjvn/modf" -l 4 -i 1.4 -a 1.8 -m stlague -PNS
python election.py -t "Ingen utjevningsmandater | Umodifisert Sainte-Laguë" -f "./figs/ingenutjvn/unmodf" -l 4 -i 1 -a 1.8 -m stlague -PNS

echo ""
echo "New counties"
python election.py -t "Nye fylker som valgdistrikt | Modifisert Sainte-Laguë" -f "./figs/nyefylker/modf" -l 4 -i 1.4 -a 1.8 -m stlague -PnS
python election.py -t "Nye fylker som valgdistrikt | Umodifisert Sainte-Laguë" -f "./figs/nyefylker/unmodf" -l 4 -i 1 -a 1.8 -m stlague -PnS

echo ""
echo "No leveling limit"
python election.py -t "Ingen sperregrense | Modifisert Sainte-Laguë" -f "./figs/sperregrense0/modf" -l 0 -i 1.4 -a 1.8 -m stlague -PS
python election.py -t "Ingen sperregrense | Umodifisert Sainte-Laguë" -f "./figs/sperregrense0/unmodf" -l 0 -i 1 -a 1.8 -m stlague -PS

echo ""
echo "3% leveling limit"
python election.py -t "Sperregrensen = 3% | Modifisert Sainte-Laguë" -f "./figs/sperregrense3/modf" -l 3 -i 1.4 -a 1.8 -m stlague -PS
python election.py -t "Sperregrensen = 3% | Umodifisert Sainte-Laguë" -f "./figs/sperregrense3/unmodf" -l 3 -i 1 -a 1.8 -m stlague -PS

echo ""
echo "4% leveling limit"
python election.py -t "Sperregrensen = 4% | Modifisert Sainte-Laguë" -f "./figs/sperregrense4/modf" -l 4 -i 1.4 -a 1.8 -m stlague -PS
python election.py -t "Sperregrensen = 4% | Umodifisert Sainte-Laguë" -f "./figs/sperregrense4/unmodf" -l 4 -i 1 -a 1.8 -m stlague -PS

echo ""
echo "5% leveling limit"
python election.py -t "Sperregrensen = 5% | Modifisert Sainte-Laguë" -f "./figs/sperregrense5/modf" -l 5 -i 1.4 -a 1.8 -m stlague -PS
python election.py -t "Sperregrensen = 5% | Umodifisert Sainte-Laguë" -f "./figs/sperregrense5/unmodf" -l 5 -i 1 -a 1.8 -m stlague -PS

echo ""
echo "American ways (FPTP WTA)"
python election.py -t "First Past The Post | norsk mandatfordeling" -f "./figs/usaway/stdmandater" -l 4 -i 1.4 -a 1.8 -m fptp -PNS
python election.py -t "First Past The Post | amerikansk mandatfordeling" -f "./figs/usaway/usamandater" -l 4 -i 1 -a 1.8 -m fptp -PUNS

echo ""
echo "Couchvoter party"
python election.py -t "Hjemmesitterne har et eget parti" -f "./figs/hjemmesitterne/hjem" -l 4 -i 1.4 -a 1.8 -m stlague -CPS
python election.py -t "Hjemmesitterne har et eget parti og sperregrensen er 3%" -f "./figs/hjemmesitterne/hjemsg3" -l 3 -i 1.4 -a 1.8 -m stlague -CPS
python election.py -t "Hjemmesitterne og blanke har et eget parti sammen" -f "./figs/hjemmesitterne/hjemblank" -l 4 -i 1.4 -a 1.8 -m stlague -CcbPS