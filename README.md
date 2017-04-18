# OCN_AOJQ_scripts

- **interface_perfil_adcp.py**
Rotina para plotar perfil de corrente de dados provenientes de ADCP.
Com a interface aberta necessário escolher o Banco e UCD para consulta.
Permite escolha de colormap para plot da intensidade e direção.


- **IDENTIFICADOR_UCD.py**
Rotina para encontrar ID das UCDs.
Com a interface aberta necessário escolher o Banco e UCD para consulta.


- **PyConfronto.py**
Rotina para gerar representações gráficas de confronto de dados 
meteo-oceanográficos aquisitados. Com a interface aberta necessário 
selecionar todos itens (Banco, UCD, Parâmetro e Sensor) para o plot.


- **embending_ocn.py**
Start a regular IPython session at any point in your program.
This allows you to evaluate dynamically the state of your code,
operate with your variables, analyze them, etc. Note however that
any changes you make to values while in the shell do not propagate
back to the running code, so it is safe to modify your values because
you won’t break your code in bizarre ways by doing so.


- **00_plot_vaisala_edinc_ES7936.py**
Rotina para plot de dados provenientes da Vaisala. Uso do tkinter para gerar
a figura dos dados recebidos via porta serial.
