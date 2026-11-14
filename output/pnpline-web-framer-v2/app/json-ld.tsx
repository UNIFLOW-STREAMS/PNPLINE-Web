import {serializeStructuredData} from './structured-data';

export default function JsonLd({data}: {data: unknown}) {
  return <script type="application/ld+json" dangerouslySetInnerHTML={{__html: serializeStructuredData(data)}}/>;
}
