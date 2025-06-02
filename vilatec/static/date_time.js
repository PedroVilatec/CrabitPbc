function date_time(id)
{
        date = new Date;
        year = date.getFullYear();
        month = date.getMonth();
        months = new Array('Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro');
        d = date.getDate();
        day = date.getDay();
        days = new Array('Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado');
        h = date.getHours();
        if(h<10)
        {
                h = "0"+h;
        }
        m = date.getMinutes();
        if(m<10)
        {
                m = "0"+m;
        }
        s = date.getSeconds();
        if(s<10)
        {
                s = "0"+s;
        }
        //result = ''+days[day]+', '+d+ ' de '+months[month] + ' de '+year+' | '+h+':'+m+':'+s;
        if(month < 10) {
            result = +d+'/0'+ (month+1) + '/'+ year +' | '+h+':'+m+':'+s;
        } else {
            result = +d+'/'+ (month+1) + '/'+ year +' | '+h+':'+m+':'+s;
        }
        document.getElementById(id).innerHTML = result;
        setTimeout('date_time("'+id+'");','1000');
        return true;
}