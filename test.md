# Test Page

__
sample code 1:
__

{% for tag in site.tags %}
  <h3>{{ tag[0] }}</h3>
  <ul>
    {% for post in tag[1] %}
      <li><a href="{{ site.baseurl }}/{{ post.url }}">{{ post.title }}</a></li>
    {% endfor %}
  </ul>
{% endfor %}


__
sample code 2:
__

{% assign sorted_tags = site.tags | sort %}
{% for tag in sorted_tags %}
{% assign vids = tag[1] | sort %}

{% if vids != empty %}

  <h2 id="{{tag[0] | uri_escape | downcase}}">{{tag[0]}}</H2>
     <p>
      {% for p in vids %}
     <a href="/{{p.type | downcase}}/"><img src="/assets/img/{{p.type | downcase}}.png" alt="{{p.type}}" title="{{p.type}}"/></a> <a href="{{ p.url }}">{{ p.title }}</a> ({{p.type}}/{{p.category}}) &raquo;  <span class="entry-date"><time datetime="{{ p.date | date_to_xmlschema }}" itemprop="datePublished">{{ p.date | date: "%B %d, %Y" }}</time></span>
     <br />
      {% endfor %}
    </p>
  
{% endif %}

{% endfor %}

__
sample code 3:
__
{% for post in site.tags.TTR %}
<h2>{{ post.title }}</h2>

{{ post.excerpt }}

{{ post.date }}
{% endfor %}



__
sample code: 4
___
<ul>
  {% for post in site.posts %}
    <li>
	<a href="{{ site.baseurl }}/{{ post.url }}"></a>
      {{ post.excerpt }}
    </li>
  {% endfor %}
</ul>






