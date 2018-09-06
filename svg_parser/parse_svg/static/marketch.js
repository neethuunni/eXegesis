var Marketch = function(obj){
  this.cache = {
    //当前选中的节点
    selected: null,
    //mouseover节点
    target: null
  };
  this.sketchData = obj.sketchData;
  //当前画板id
  this.currentArtboardId = null;
  //当前画板所有图层数据
  this.currentAbData = {};
  this.unit = {};
  //是否显示切片
  this.showSlice = false;
  //语言
  this.language = obj.sketchData.language;
  //多语言
  this.I18N = obj.sketchData.I18N;
  //Symbols
  this.symbols = {};
  //创建dom(替换I18N)
  this.setup();
};

Marketch.prototype = {
  setup: function(){
    var html = $('#page textarea').val();

    $.each(this.I18N, function(key, value){
      var reg = new RegExp('{'+ key +'}', 'g');
      html = html.replace(reg, value);
    });

    $('#page').html(html);
    $('html').addClass('lan-'+ this.language);
  },

  render: function(){
    //创建选中图层的标注
    this.buildMarker();
    //创建虚线导航灯塔
    this.buildLighthouse();
    //创建2个图层之间的标尺
    this.buildRuler();
    //slice导出选项
    this.buildSliceNav();
    this.bind();
    this.buildList();
  },

  buildSliceNav: function(){
    var html = [];

    html.push(
      '<div id="sk-slice" class="sk-slice">',
        '<a title="', this.I18N['DRAGTOSAVE'] ,'" target="_blank" href="#"><img src="about:blank" /><span>@1x</span></a>',
        '<a title="', this.I18N['DRAGTOSAVE'] ,'" target="_blank" href="#"><img src="about:blank" /><span>@2x</span></a>',
      '</div>'
    );

    $('#wrap').append(html.join(''));
  },

  //创建选中图层的标注
  buildMarker: function(){
    var marker = $('<div>');
    marker.attr({
      id: 'sketch-marker',
      class: 'sketch-marker'
    });
    marker.html('<b class="skm-w" w=""></b><b class="skm-h" h=""></b><span class="skm-tl"></span><span class="skm-tr"></span><span class="skm-bl"></span><span class="skm-br"></span>');

    $('#wrap').append(marker);
  },

  //创建虚线导航灯塔（选中图层后标识当前图层位置的虚线框）
  buildLighthouse: function(){
    var html = [];

    html.push(
      '<div id="skl-top" class="skl-top"></div>',
      '<div id="skl-bottom" class="skl-bottom"></div>',
      '<div id="skl-left" class="skl-left"></div>',
      '<div id="skl-right" class="skl-right"></div>'
    );

    $('#wrap').append(html.join(''));
  },

  //显示或隐藏虚线导航灯塔(根据cache.selected判断)
  changeLightHouseState: function(){
    var topEl = $('#skl-top');
    var bottomEl = $('#skl-bottom');
    var leftEl = $('#skl-left');
    var rightEl = $('#skl-right');
    var selected = this.cache.selected;
    var position = null;
    var artboard = null;

    if(!this.cache.selected){
      topEl.hide();
      bottomEl.hide();
      leftEl.hide();
      rightEl.hide();
    }else{
      position = selected.position();
      artboard = selected.parents('.wrap-layer');

      topEl.css({
        display: 'block',
        top: position.top,
        width: artboard.width()
      });
      bottomEl.css({
        display: 'block',
        top: position.top + selected.height(),
        width: artboard.width()
      });
      leftEl.css({
        display: 'block',
        left: position.left,
        height: artboard.height()
      });
      rightEl.css({
        display: 'block',
        left: position.left + selected.width(),
        height: artboard.height()
      });
    }
  },

  //创建2个图层之间的标尺
  buildRuler: function(){
    var frageElement = document.createDocumentFragment();
    var className = ['skm-r-top', 'skm-r-right', 'skm-r-bottom', 'skm-r-left']

    for(var i=0,len=className.length;i<len;i++){
      var node = document.createElement('div');
      node.id = className[i];
      node.className = 'skm-rule '+ className[i];
      node.innerHTML = '<span></span>';

      frageElement.appendChild(node)
    }

    $('#wrap').append(frageElement);
  },

  decode: function(str){
    return decodeURIComponent(str).replace(/^\s+|\s+$/g, '');
  },

  //页面切换 old: buildSwitch
  buildList: function(){
    var self = this;
    var aside = $("#aside");
    var pageListHtml = [];
    var currentPageId = null;
    //切换单位select
    var unitMap = {
      standard: {
        unit: "px",
        factor: 1
      },
      points: {
        unit: "pt",
        factor: 1
      },
      retina: {
        unit: "pt",
        factor: 2
      },
      retinahd: {
        unit: "pt",
        factor: 3
      },
      ldpi: {
        unit: "dp",
        factor: 0.75
      },
      mdpi: {
        unit: "dp",
        factor: 1
      },
      hdpi: {
        unit: "dp",
        factor: 1.5
      },
      xhdpi: {
        unit: "dp",
        factor: 2
      },
      xxhdpi: {
        unit: "dp",
        factor: 3
      },
      xxxhdpi: {
        unit: "dp",
        factor: 4
      }
    };

    pageListHtml.push('<ul class="page-list">');

    $.each(self.sketchData.pageOrder, function(index, pageId){
      var data = self.sketchData.pageData[pageId];
      var title = self.decode(data.name);
      var artboardCount = 0;

      if(!/^-{1}[^-]*?.*$/.test(title)){
        pageListHtml.push(
          '<li data-page="'+ data.pageId +'">'
        );

        if(index == 0){
          currentPageId = data.pageId;
        }

        for(var i=data.artboardId.length-1; i>=0; i--){
          var artboardId = data.artboardId[i];
          var artboradData = self.sketchData.artboard[artboardId];
          var artboardName = self.decode(artboradData.name);

          if(artboradData.symbolId){
            self.symbols[artboradData.symbolId] = artboradData;
          }

          if(!/^-{1}[^-]*?.*$/.test(artboardName)){
            artboardCount++;
          }
        }

        if(artboardCount > 0){
          pageListHtml.push('<h2 class="more" title="' + title + '"><span>'+ title + '</span></h2><ul class="ab-list">');

          for(var i=data.artboardId.length-1; i>=0; i--){
            var artboardId = data.artboardId[i];
            var artboradData = self.sketchData.artboard[artboardId];
            var artboardName = self.decode(artboradData.name);

            if(!/^-{1}[^-]*?.*$/.test(artboardName)){
              artboardCount++;

              pageListHtml.push(
                '<li data-ab="'+ artboradData.id +'"><h3 title="' + artboardName + '">'+ artboardName +'</h3></li>'
              );
            }
          }

          pageListHtml.push('</ul></li>');
        }
      }
    });

    pageListHtml.push('</ul>');
    aside.html(pageListHtml.join(''));

    //切换画板
    $("#aside h3").on('click', function(e){
      var el = $(this).parent();
      var artboardId = el.attr('data-ab');
      var selectArtData = self.sketchData.artboard[artboardId];
      $('#aside .page-active').removeClass('page-active');
      $('#aside .art-active').removeClass('art-active');
      el.addClass('art-active');
      el.parents('li').addClass('page-active')
      self.cache.selected = null;

      //隐藏标记
      $('#sketch-marker').css('visibility', 'hidden');
      $('#panel').removeClass('panel-active');
      $('#wrap').width($('#wrap').attr('data-width'));

      self.changeLightHouseState();
      //加载目标画板
      self.loadArtboard(selectArtData);
    }).eq(0).click();

    $("#unit").on('click', function() {
      var dropdown = $(this).siblings(".dropdown");
      $(this).toggleClass("active");
      dropdown.toggleClass("active");
    });

    $('#sk-slice').on('click', function(e){
      e.stopPropagation();
    });

    //切换单位
    $("#dropdown").on('click', function(e) {
      e.stopPropagation();
      $(this).removeClass("active");

      if($(e.target).is($('#dropdown'))){
        return false;
      }

      var unit = $(e.target).attr("data-value");
      var text = $(e.target).text();
      $('#unit').find('.unit-current').text(text).end().removeClass('active');

      self.unit = unitMap[unit];
      if (self.cache.selected) {
        self.selectedLayer();
        self.showPanel();
      }
    }).children().first().click();
  },

  //加载画板
  loadArtboard: function(artboard){
    var self = this;
    var artboardId = artboard.id;
    var targetEl = $('#'+ artboardId);
    var baseX = artboard.x;
    var baseY = artboard.y;
    var artHtml = [];

    //保存当前画板id
    self.currentArtboardId = artboardId;

    //切换图层默认不现实切片
    self.showSlice = false;
    $('#wrap').removeClass('wrap-slice-active');
    //存在切片时显示切片
    if(this.sketchData.exportEveryLayer && artboard.slice && artboard.slice.length > 0){
      $('#hd-slice').show();
    }else{
      $('#hd-slice').hide().find('input').get(0).checked = false;;
    }
    if(targetEl.length == 0){
      targetEl = $('<div>');
      targetEl.attr('id', artboardId);

      //普通图层
      $.each(artboard.layer, function(index, layer){
        var x = layer.x;
        var y = layer.y;
        var layerWidth = layer.width;
        var layerHeight = layer.height;

        self.currentAbData[layer.id] = layer;

        if(layer.symbolId){
          artHtml.push(
            self.buildSymbolArtboard(layer, (layer.x - baseX), (layer.y - baseY))
          );
        }else{
          if(layer.borderWidth){
            layerWidth += layer.borderWidth * 2;
            layerHeight += layer.borderWidth * 2;
          }

          //位置和尺寸都要像左上方移动1px，避免测量准确的问题
          artHtml.push(
            '<div class="art-layer" id="', layer.id ,'" style="',
              'position:absolute;top:', (layer.y - baseY) ,'px;',
              'z-index:', layer.zIndex , ';',
              'left:', (layer.x - baseX) ,'px;',
              'width: ', layerWidth, 'px;',
              'height: ', layerHeight, 'px;',
            '" name="', self.decode(layer.name) ,'">',
              //layer.html,
            '</div>'
          );
        }
      });

      //slice图层
      artboard.slice && $.each(artboard.slice, function(index, sliceLayer){
        var x = sliceLayer.x;
        var y = sliceLayer.y;

        self.currentAbData[sliceLayer.id] = sliceLayer;

        //位置和尺寸都要像左上方移动1px，避免测量准确的问题
        artHtml.push(
          '<div class="art-slice" id="', sliceLayer.id ,'" style="',
            'position:absolute;top:', (sliceLayer.y - baseY) ,'px;',
            'z-index:', sliceLayer.zIndex , ';',
            'left:', (sliceLayer.x - baseX) ,'px;',
            'width: ', sliceLayer.width, 'px;',
            'height: ', sliceLayer.height, 'px;',
            '" name="', self.decode(sliceLayer.name) ,'">',
            //layer.html,
          '</div>'
        );
      });

      artHtml.push('</div>');

      targetEl.attr('class', 'wrap-layer').html(artHtml.join('')).css({
        width: artboard.width,
        height: artboard.height,
        background: 'url('+'/exegesis/static/sketches/'+ artboard.id +'/artboard.png)'
      }).appendTo($('#wrap'));

      self.resetMask({
        maskData: artboard.mask
      });
    }

    $('#wrap .wrap-layer-active').removeClass('wrap-layer-active');
    targetEl.addClass('wrap-layer-active');

    $('#wrap').css({width: targetEl.width() + 220}).parent().scrollLeft(0);
  },

  buildSymbolArtboard: function(symbolLayer, symbolX, symbolY){
    var self = this;
    var symbolData = self.symbols[symbolLayer.symbolId];
    var artHtml = [];
    var baseX = symbolData && symbolData.x;
    var baseY = symbolData && symbolData.y;

    symbolData && $.each(symbolData.layer, function(index, layer){
      var x = layer.x;
      var y = layer.y;
      var layerWidth = layer.width;
      var layerHeight = layer.height;

      self.currentAbData[layer.id] = layer;

      if(layer.symbolId){
        artHtml.push(
          self.buildSymbolArtboard(layer, (layer.x - baseX), (layer.y - baseY))
        );
      }else{
        if(layer.borderWidth){
          layerWidth += layer.borderWidth * 2;
          layerHeight += layer.borderWidth * 2;
        }

        //位置和尺寸都要像左上方移动1px，避免测量准确的问题
        artHtml.push(
          '<div class="art-layer" id="', layer.id ,'" style="',
            'position:absolute;top:', (layer.y - baseY + symbolY) ,'px;',
            'z-index:', layer.zIndex , ';',
            'left:', (layer.x - baseX + symbolX) ,'px;',
            'width: ', layerWidth, 'px;',
            'height: ', layerHeight, 'px;',
          '" name="', self.decode(layer.name) ,'">',
            //layer.html,
          '</div>'
        );
      }
    });

    return artHtml.join('');
  },

  /**
   * 交换maskzIndex
   * @param obj.maskData mask数据
   * @return
   */
  resetMask: function(obj){
    $.each(obj.maskData, function(maskId, childItem){
      var maskLayers = [];
      //起始zindex值
      var startZindex = parseInt($('#'+ maskId).css('zIndex'), 10);
      //filer not exist layer(TODO: fixed the bug in export.cocoascript)
      $.each([maskId].concat(childItem), function(index, layerId){
        if($('#'+ layerId).length > 0){
          maskLayers.push(layerId);
        }
      });

      //按面积倒序
      maskLayers.sort(function(a, b){
        var elA = $('#'+ a);
        var elB = $('#'+ b)
        var widthA = elA.width() || 0;
        var heightA = elA.height() || 0;
        var widthB = elB.width() || 0;
        var heightB = elB.height() || 0;

        return (widthB * heightB) - (widthA * heightA);
      });

      //重置图层zindex
      $.each(maskLayers, function(index, layerId){
          $('#'+ layerId).css({zIndex: startZindex + index});
      });
    });
  },

  bind: function(){
    var self = this;
    var timer = {};

    $('#wrap').on('click', function(e){
      var el = $(e.target);
      var id = el.attr('id');

      if(id && self.currentAbData[id]){
        if(!self.showSlice){
          //显示图层
          if(!self.cache.selected || id != self.cache.selected.attr('id')){
            self.cache.selected = el;

            $('#sketch-marker').css('visibility', 'visible').removeClass('sketch-marker-disable');
            self.changeLightHouseState();
            self.changeRulerState('none', {});
            self.selectedLayer();
            self.showPanel();
          }
        }else{
          if(el.hasClass('art-slice')){
            var slicePath = self.currentArtboardId +'/slice/'+ self.currentAbData[id].name;
            $('#wrap .art-slice-active').removeClass('art-slice-active');
            //显示切片
            $('#sk-slice').css({
              top: el.css('top'),
              left: el.css('left')
            }).find('a').each(function(index){
              var el = $(this);
              var path = slicePath +'@1x.png'

              if(index == 1){
                path = slicePath +'@2x.png'
              }

              el.attr('href', path).find('img').attr('src', path);
            })
            el.addClass('art-slice-active');
          }
        }
      }else{
        self.cache.selected = null;

        self.changeLightHouseState();
        self.changeRulerState('none', {});

        $('#panel').removeClass('panel-active');
        $('#wrap').width($('#wrap').attr('data-width'))
        $('#wrap').find('.art-slice-active').removeClass('art-slice-active');
        $('#sketch-marker').css('visibility', 'hidden');
        $('#sk-slice').css({top:-1000, left:-1000});
      }
    })
    .on('mousemove', function(e){
      var el = $(e.target);
      var id = el.attr('id');

      if(id && (self.currentAbData[id] || el.hasClass('wrap-layer'))){
        if(self.cache.selected){
          //有被选中的图层时显示距离
          if(id != self.cache.selected.attr('id') ){
            self.cache.target = el;
            $('#sketch-marker').addClass('sketch-marker-disable');
            self.showRuler();
          }
        }else{
        }
      }else{
        self.changeRulerState('none', {});
      }
    })
    .on('mouseout', function(e){
      var el = $(e.target);
      var id = el.attr('id');

      if(id && (self.currentAbData[id] || el.hasClass('wrap-layer'))){
        $('#sketch-marker').removeClass('sketch-marker-disable');
        self.cache.target = null;
        self.changeRulerState('none', {});
      }
    });

    $('#panel').on('change', function(e){
      var el = $(e.target);
      if(el.get(0).nodeName.toLowerCase() == 'select'){
        var type = el.attr('name');

        if(type = 'format'){
          //修改导出类型
          if(el.val() == 'svg'){
            $('#panel').find('select[name=size]').attr('disabled', 'disabled');
          }else{
            $('#panel').find('select[name=size]').removeAttr('disabled');
          }
        }

        if(type == 'size' || type == 'format'){
          //修改导出图片路径
          var base = $('#export-btn').data('base');
          var baseName = $('#export-btn').data('name');
          var exportScale = $('#panel').find('select[name=size]').val();
          var exportType = $('#panel').find('select[name=format]').val();
          var link = ''
          var name = ''

          if(exportType == 'svg'){
            link = base +'.svg';
            name = baseName + '.svg';
          }else{
            link = base +'@'+ exportScale +'.png';
            name = baseName +'@'+ exportScale +'.png';
          }
          $('#export-btn').attr('href', link).attr('download', name);
        }
      }
    }).on('dblclick', function(e){
      var el = $(e.target);
      var name = '';

      if(e.target.nodeName.toLowerCase() == 'textarea'){
        name = el.attr('name');
        el.select();
        document.execCommand('copy');
        //复制成功的提示
        el.parents('dl').addClass('copy-success');
        timer[name] = setTimeout(function(){
          el.parents('dl').removeClass('copy-success');
        }, 1000);
      }

      if(el.parents('.pa-symbol').length > 0){
        var symbolId = el.parents('.pa-symbol').data('symbolid');
        var symbolData = self.symbols[symbolId];

        if($('#aside li[data-ab='+ symbolData.id +']')){
          var theNav = $('#aside li[data-ab='+ symbolData.id +']');
          theNav.find('h3').click();
        }
      }
    })

    $('body').on('click', function(e) {
      if (!($(e.target).hasClass('unit') || $(e.target).parent().hasClass('unit'))) {
        $('.dropdown').removeClass('active');
        $('.unit').removeClass('active');
      }
    });

    //切换图层&&slice
    $('#hd-slice input').click(function(){
      if(this.checked){
        self.showSlice = true;
        $('#wrap').addClass('wrap-slice-active');
      }else{
        self.showSlice = false;
        $('#wrap').removeClass('wrap-slice-active');
      }
      $('#wrap').click();
    });
  },

  //选中图层
  selectedLayer: function(){
    var marker = this.cache.marker;
    var selected = this.cache.selected;
    var width = selected.outerWidth();
    var height = selected.outerHeight();
    var position = selected.position();

    $('#sketch-marker').css({
      width: width,
      height: height,
      top: position.top,
      left: position.left,
      visibility: 'visible'
    }).find('b').eq(0).attr('w', this.getScale(parseInt(width, 10)))
      .end().eq(1).attr('h', this.getScale(parseInt(height, 10)))
  },

  showPanel: function(){
    var selected = this.cache.selected;
    var objectId = selected.attr('id');
    var layerData = this.currentAbData[objectId];

    var html = [];

    html.push(
      '<dl class="pa-block">',
        '<dt><h2>', this.decode(layerData.name), '</h2></dt>',
      '</dl>',
      '<dl class="pa-block">',
        '<dt><span>Position & Size</span></dt>',
        '<dd>',
          '<ul>',
            '<li><input value="', this.getScale(layerData.x) ,'" readonly><label>X</label></li>',
            '<li><input value="', this.getScale(layerData.y) ,'" readonly><label>Y</label></li>',
            '<li><input value="', this.getScale(layerData.width) ,'" readonly><label>', this.I18N['WIDTH'] ,'</label></li>',
            '<li><input value="', this.getScale(layerData.height) ,'" readonly><label>', this.I18N['HEIGHT'] ,'</label></li>',
          '</ul>',
        '</dd>',
      '</dl>'
    );

    if(layerData.border){
      html.push(
        '<dl class="pa-inline">',
          '<dt><span>', this.I18N['border'] ,'</span></dt>',
          '<dd>',
            '<ul>',
              '<li><label>', this.I18N['size'] ,'</label>', this.getScale(layerData.border.width) ,'</li>',
              '<li><label>', this.I18N['color'] ,'</label>', layerData.border.color ,'</li>',
            '</ul>',
          '</dd>',
        '</dl>'
      )
    }

    if(layerData.background){
      html.push(
        '<dl class="pa-inline pa-fill">',
          '<dt><span>', this.I18N['FILLCOLOR'] ,'</span></dt>',
          '<dd>',
            '<p>', layerData.background , '<span style="background-color:', layerData.background, ';"></span></p>',
          '</dd>',
        '</dl>'
      )
    }

    if(layerData.radius){
      html.push(
        '<dl class="pa-inline">',
          '<dt><span>', this.I18N['RADIUS'] ,'</span></dt>',
          '<dd>',
            '<p>', layerData.radius ,'</p>',
          '</dd>',
        '</dl>'
      )
    }

    if(layerData.sharedStyle != ''){
      html.push(
        '<dl class="pa-block">',
          '<dt><span>', this.I18N[layerData.sharedStyleType] ,'</span></dt>',
          '<dd>',
            '<textarea name="content" readonly>', layerData.sharedStyle ,'</textarea>',
          '</dd>',
        '</dl>'
      )
    }

    //文字图层显示内容及字号
    if(layerData.html){
      //内容块
      html.push(
        '<dl class="pa-block">',
          '<dt><span>', this.I18N['LAYERTEXT'] ,'</span><em>', this.I18N['COPYSUCCESS'] ,'</em></dt>',
          '<dd>',
            '<textarea name="content">', this.decode(layerData.html) ,'</textarea>',
          '</dd>',
        '</dl>'
      );

      //字号块：根据用户选择转换单位
      html.push(
        '<dl class="pa-block">',
          '<dt><span>', this.I18N['FONTSIZE'] ,'</span><em>', this.I18N['COPYSUCCESS'] ,'</em></dt>',
          '<dd>',
            '<textarea name="fontSize">', this.getScale(layerData.style["font-size"]) ,'</textarea>',
          '</dd>',
        '</dl>'
      );
    }

    if(layerData.style){
      html.push(
        '<dl class="pa-block">',
          '<dt><span>', this.I18N['CODE'] ,'</span><em>', this.I18N['COPYSUCCESS'] ,'</em></dt>',
          '<dd>',
            '<textarea name="code">', this.formatStyle(layerData.style) ,'</textarea>',
          '</dd>',
        '</dl>'
      )
    }

    if(layerData.symbolId){
      var symbolData = this.symbols[layerData.symbolId];
      html.push(
        '<dl class="pa-block pa-symbol" data-symbolid="', layerData.symbolId ,'">',
          '<dd>',
            '<span><img height="15" src="', symbolData.id, '/artboard.png" /></span>',
            '<em>', symbolData.name, '</em>',
          '</dd>',
        '</dl>'
      )
    }

    if(!layerData.html && this.sketchData.exportEveryLayer){
      var formatType = '<option value="png">png</option>';
      if(/^svg/.test(layerData.name)){
        formatType += '<option value="svg">svg</option>'
      }

      html.push(
        '<dl class="pa-block pa-export">',
          '<dt><span>', this.I18N['EXPORT'] ,'</span></dt>',
          '<dd>',
            '<ul>',
              '<li>',
                '<label>', this.I18N['SIZE'] ,'</label>',
                '<select name="size">',
                  '<option select value="1x">1x</option>',
                  '<option value="2x">2x</option>',
                  '<option value="0.5x">0.5x</option>',
                  '<option value="3x">3x</option>',
                '</select>',
              '</li>',
              '<li>',
                '<label>', this.I18N['FORMAT'] ,'</label>',
                '<select name="format">', formatType ,'</select>',
              '</li>',
            '</ul>',
            '<div class="export-btn">',
              '<a id="export-btn" href="javascript:;" data-base="', this.currentArtboardId ,'/', objectId ,'" ',
              'class="panel-export" download="" data-name="', layerData.name ,'">', this.I18N['EXPORTLAYER'] ,'</a>',
            '</div>',
          '</dd>',
        '</dl>'
      )
    }

    $('#panel').html(html.join('')).addClass('panel-active');
    //重新设置textarea高度
    $('#panel').find('textarea').each(function(){
      var height = this.scrollHeight;
      var width = this.scrollWidth;

      if(height <= 39){
        if(width > 175){
          $(this).css({height: 19});
        }
      }else if(height > 25 && height < 120){
        $(this).css({height: height});
      }else if(height > 120){
        $(this).css({height: 120});
      }
    });
    $('#wrap').width($('#wrap').attr('data-width') - 200);

    $('select').change();
  },

  //格式化css json数据
  formatStyle: function(styleJson){
    var style = [];
    for(var k in styleJson){
      style.push(k +':'+ (styleJson[k].indexOf('font-family') > -1 ? '"'+styleJson[k]+'"' : styleJson[k]) +';');
    }

    return style.join('\r\n');
  },

  //显示标尺，标尺总是由target指向selected
  changeRulerState: function(type, data){
    $('#skm-r-top').css('visibility', 'hidden');
    $('#skm-r-left').css('visibility', 'hidden');
    $('#skm-r-right').css('visibility', 'hidden');
    $('#skm-r-bottom').css('visibility', 'hidden');

    if(type == 'none'){return false;}

    //向上的标尺
    if(type.indexOf('top') > -1){
      $('#skm-r-top').css({
        left: (data.tx + data.tw/2),
        top: (data.sy + data.sh + 2),
        height: parseInt((data.ty - data.sy - data.sh - 4), 10)
      })
      .css('visibility', 'visible')
      .find('span').html(this.getScale(parseInt((data.ty - data.sy - data.sh), 10)));
    }

    //向左的标尺
    if(type.indexOf('left') > -1){
      $('#skm-r-left').css({
        top: (data.ty + data.th/2),
        left: (data.sx + data.sw + 2),
        width: parseInt((data.tx - data.sx - data.sw - 4), 10)
      })
      .css('visibility', 'visible')
      .find('span').html(this.getScale(parseInt((data.tx - data.sx - data.sw), 10)));
    }

    //向右的标尺
    if(type.indexOf('right') > -1){
      $('#skm-r-right').css({
        top: (data.ty + data.th/2),
        left: (data.tx + data.tw + 2),
        width: parseInt((data.sx - data.tx - data.tw - 4), 10)
      })
      .css('visibility', 'visible')
      .find('span').html(this.getScale(parseInt((data.sx - data.tx - data.tw), 10)));
    }

    //向下的标尺
    if(type.indexOf('bottom') > -1){
      $('#skm-r-bottom').css({
        left: (data.tx + data.tw/2),
        top: (data.ty + data.th + 2),
        height: parseInt((data.sy - data.ty - data.th - 4), 10)
      })
      .css('visibility', 'visible')
      .find('span').html(this.getScale(parseInt((data.sy - data.ty - data.th), 10)));
    }

    //鼠标图层(t)包含选中图层(s)
    if(type == 'container-in'){
      $('#skm-r-top').css({
        left: (data.sx + data.sw/2),
        top: (data.ty + 1),
        height: parseInt((data.sy - data.ty - 3), 10)
      })
      .css('visibility', 'visible')
      .find('span').html(this.getScale(parseInt((data.sy - data.ty), 10)));

      $('#skm-r-bottom').css({
        left: (data.sx + data.sw/2),
        top: (data.sy + data.sh + 2),
        height: this.validateNum(data.ty + data.th - data.sy - data.sh - 2)
      })
      .css('visibility', 'visible')
      .find('span').html(this.getScale(this.validateNum(data.ty + data.th - data.sy - data.sh)));

      $('#skm-r-left').css({
        top: (data.sy + data.sh/2),
        left: (data.tx + 1),
        width: parseInt(this.validateNum(data.sx - data.tx - 3), 10)
      })
      .css('visibility', 'visible')
      .find('span').html(this.getScale(parseInt((data.sx - data.tx), 10)));

      $('#skm-r-right').css({
        top: (data.sy + data.sh/2),
        left: (data.sx + data.sw + 2),
        width: this.validateNum(data.tx + data.tw - data.sx - data.sw - 3)
      })
      .css('visibility', 'visible')
      .find('span').html(this.getScale(this.validateNum(data.tx + data.tw - data.sx - data.sw)));
    }

    //被选中图层(s)包含鼠标图层(t)
    if(type =='container-out'){
      $('#skm-r-top').css({
        left: (data.tx + data.tw/2),
        top: (data.sy + 1),
        height: this.validateNum(data.ty - data.sy - 3)
      })
      .css('visibility', 'visible')
      .find('span').html(this.getScale(this.validateNum(data.ty - data.sy)));

      $('#skm-r-bottom').css({
        left: (data.tx + data.tw/2),
        top: (data.ty + data.th + 2),
        height: this.validateNum(data.sy + data.sh - data.ty - data.th - 3)
      })
      .css('visibility', 'visible')
      .find('span').html(this.getScale(this.validateNum(data.sy + data.sh - data.ty - data.th)));

      $('#skm-r-left').css({
        top: (data.ty + data.th/2),
        left: (data.sx + 1),
        width: this.validateNum(data.tx - data.sx - 3)
      })
      .css('visibility', 'visible')
      .find('span').html(this.getScale(this.validateNum(data.tx - data.sx)));

      $('#skm-r-right').css({
        top: (data.ty + data.th/2),
        left: (data.tx + data.tw + 2),
        width: this.validateNum(data.sx + data.sw - data.tx - data.tw - 3)
      })
      .css('visibility', 'visible')
      .find('span').html(this.getScale(this.validateNum(data.sx + data.sw - data.tx - data.tw)));
    }
  },

  validateNum: function(num){
    return num < 0 ? parseInt(Math.abs(num), 10) : parseInt(num, 10);
  },

  getScale: function(pixel) {
    var pixelNum = parseInt(pixel, 10);
    var scales = {
      px: pixelNum + 'px',
      pt: pixelNum * 0.75 / this.unit.factor + 'pt',
      dp: pixelNum / this.unit.factor + 'dp'
    }

    return scales[this.unit.unit];
  },

  /*
   * 显示标记T表示当前鼠标over的图层，S表示选中的图层
   * 标尺总是由target指向selected
   *  T1     T2
   *   ┌     ┐
   *      S
   *   └     ┘
   *  T3     T4
   */
  showRuler: function(){
    var buffer = 0;
    //当前选中的节点
    var selectEl = this.cache.selected;
    //mouseover目标节点
    var targetEl = this.cache.target;
    var data = {
      //选中节点宽
      sw: selectEl.width(),
      //选中节点高
      sh: selectEl.height(),
      //选中节点x坐标
      sx: selectEl.position().left,
      //选中节点y坐标
      sy: selectEl.position().top,
      //mouseover节点宽
      tw: targetEl.width(),
      //mouseover节点高
      th: targetEl.height(),
      //mouseover节点x坐标
      tx: targetEl.position().left,
      //mouseover节y坐标
      ty: targetEl.position().top
    }

    //鼠标经过的图层在选中图层上方(T1 T2的位置)
    if(data.sy - (data.ty + data.th) >= buffer){
      if(data.sx - (data.tx + data.tw) >= buffer){
        //[上]左 显示向下，向右的标尺
        this.changeRulerState('bottom-right', data);
      }else if(data.tx - (data.sx + data.sw) >= buffer){
        //[上]右 显示向下，向左的标尺
        this.changeRulerState('bottom-left', data);
      }else{
        this.changeRulerState('bottom', data);
      }
    }

    //鼠标经过的图层在选中图层下方(T1 T2的位置)
    if(data.ty - (data.sy + data.sh) > buffer){
      if(data.sx - (data.tx + data.tw) >= buffer){
        //[下]左 显示向上，向右的标尺
        this.changeRulerState('top-right', data);
      }else if(data.tx - (data.sx + data.sw) >= buffer){
        //[下]右 显示向上，向左的标尺
        this.changeRulerState('top-left', data);
      }else{
        this.changeRulerState('top', data);
      }
    }

    //鼠标经过的图层与选中图层映射到垂直线上有交集只显示水平的标尺
    if((data.ty >= data.sy && data.ty <= (data.sy + data.sh)) || (data.sy >= data.ty && data.sy <= (data.ty + data.th))){
      if(data.sx - (data.tx + data.tw) >= buffer){
        this.changeRulerState('right', data);
      }else if(data.tx - (data.sx + data.sw) >= buffer){
        this.changeRulerState('left', data);
      }else{
        //鼠标图层(t)包含选中图层(s)(标尺总是由target指向selected)
        this.changeRulerState('container-in', data);
      }
    }

    //鼠标经过的图层与选中图层映射到水平线上有交集只显示垂直的标尺
    if(data.tx >= data.sx && data.tx <= (data.sx + data.sw)){
      if(data.sy - (data.ty + data.th) >= buffer){
        this.changeRulerState('bottom', data);
      }else if(data.ty - (data.sy + data.sh) >= buffer){
        this.changeRulerState('top', data);
      }else{
        //被选中图层(s)包含鼠标图层(t)(标尺总是由target指向selected)
        this.changeRulerState('container-out', data);
      }
    }
  }
}


window.onload = function(){
  var xdata = document.createElement('script');
  new Marketch({
    sketchData: pageData
  }).render();
	xdata.src = 'data.js';
	document.body.appendChild(xdata);
}