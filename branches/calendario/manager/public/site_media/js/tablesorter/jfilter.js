$.tablesorter.addWidget({
	id: 'jFilter',
	format: function(element){
		var __jFilter = this;
		$(element).before('<input type="text" value="" id="filter-for-'+$(element).attr('id')+'" rel="'+$(element).attr('id')+'">');
		$('#filter-for-'+$(element).attr('id')).bind('keyup',function(ev){
			__jFilter.jFilterRun(element,$('#filter-for-'+$(element).attr('id')).val());
		});
	},
	jFilterRun: function(table, s){
		$('tbody tr:hidden', table).show();
		$('tbody tr',$(table)).each(function(n,r){
			var content = false;
			$('td',$(r)).each(function(i,f){
				if (($(f).html() || $(f).text()).toLowerCase().indexOf(s.toLowerCase()) >= 0)
					content = true;
			});
			if (content) $(r).show(); else $(r).hide();
		});
		}
});
