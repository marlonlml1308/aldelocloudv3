<?php

namespace App\Filament\Resources;

use App\Filament\Resources\ProductResource\Pages;
use App\Filament\Resources\ProductResource\RelationManagers;
use App\Models\Products;
use App\Models\Taxes;
use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Enums\FiltersLayout;
use Filament\Tables\Filters\SelectFilter;
use Filament\Tables\Filters\TernaryFilter;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletingScope;
use Illuminate\Support\Facades\DB;

class ProductResource extends Resource
{
    protected static ?string $model = Products::class;
    protected static ?string $navigationGroup = 'Menu';
    protected static ?string $navigationIcon = 'heroicon-o-shopping-cart';

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\TextInput::make('menuitemtext')
                ->label('Producto')
                ->required()
                ->maxLength(14)
                ->dehydrateStateUsing(fn (string $state) => strtoupper($state))
                ->rule(function (string $operation, ?Model $record = null) {
                    return function ($attribute, $value, $fail) use ($operation, $record) {
                        if ($value !== null) {
                            $query = DB::table('products')
                                ->where('menuitemtext', $value);
                            if ($operation === 'edit' && $record) {
                                $query->where('id', '!=', $record->id);
                            }
                            $exists = $query->exists();
                            if ($exists) {
                                $fail('El nombre ya está en uso. Debe ser único.');}
                        }
                    };
                }),
                Forms\Components\Select::make('menucategoryid')->label('Categoria')
                ->required()
                ->relationship(name: 'Categories', titleAttribute: 'menucategorytext'),
                Forms\Components\Select::make('menugroupid')->label('Grupo')
                ->required()
                ->relationship(name: 'Groups', titleAttribute: 'menugrouptext'),
                Forms\Components\TextInput::make('defaultunitprice')
                ->label('Precio')
                ->numeric()
                ->required()
                ->maxLength(8) // Restringe la longitud del texto
                ->prefix('$') // Agrega el símbolo de moneda
                ->extraInputAttributes([
                    'step' => '0.01', // Permite valores con dos decimales
                    'min' => '0', // Evita números negativos
                    'maxlength' => '8', // Asegura que el usuario no escriba más de 8 caracteres
                ])
                ->live(),
                Forms\Components\Toggle::make('menuiteminactive')
                ->label('Inactivo')
                ->required(),
                Forms\Components\Toggle::make('menuitemtaxable')
                ->label(fn () => Taxes::getTaxName(1)),
                Forms\Components\Toggle::make('gstapplied')
                    ->label(fn () => Taxes::getTaxName(2)),
                Forms\Components\Toggle::make('liquortaxapplied')
                    ->label(fn () => Taxes::getTaxName(3)),
                Forms\Components\Select::make('displayindex')
                ->label('Posicion')
                ->required()
                ->options(function (string $operation, ?Model $record = null) {
                    $query = DB::table('groups')
                        ->where('menugroupinactive', '!=', true)
                        ->pluck('displayindex');
                    if ($operation === 'edit' && $record) {
                        $query = $query->filter(fn ($value) => $value != $record->displayindex);
                    }
                    $allPossibleValues = range(-1, 31);
                    $availableValues = collect($allPossibleValues)
                        ->filter(function ($value) use ($query) {
                            return !$query->contains($value);
                        })
                        ->mapWithKeys(function ($value) {
                            return [$value => $value === -1 ? 'Inactivo o subplatillo (-1)' : "Posición {$value}"];
                        })
                        ->toArray();

                    return $availableValues;
                })
                ->searchable()
                ->preload(),
                Forms\Components\Toggle::make('menuiteminstock')
                ->label('En Stock')
                ->required()
                ->default(true)
                ->inline(false),
                Forms\Components\Toggle::make('menuitemdiscountable')
                ->label('Descontable')
                ->required()
                ->default(true)
                ->inline(false),
                Forms\Components\Select::make('menuitemtype')
                ->label('Tipo de Producto')
                ->options([
                    1 => 'Producto',
                    2 => 'Platillo Superior',
                ])
                ->default(1) // Valor por defecto "Producto"
                ->required()
                ->live() // Hace que el cambio se detecte en tiempo real
                ->afterStateUpdated(function ($state, callable $set) {
                    if ($state == 2) { // Si es "Platillo Superior"
                        $set('displayindex', -1); // Cambia la posición a -1
                        $set('defaultunitprice', 0); // Cambia el precio a 0
                    }
                }),
                Forms\Components\Select::make('menuitempopupheaderid')
                ->label('Producto Padre')
                ->options(fn ($get) => Products::where('id', '!=', $get('id')) // Excluye el producto actual
                    ->pluck('menuitemtext', 'id')
                    ->toArray())
                ->searchable() // Permite buscar dentro del select
                ->preload() // Carga los datos antes de abrir el select
                ->nullable(), // Permite no seleccionar un valor
                Forms\Components\Select::make('gaspump')
                ->label('Exento de Impuestos')
                ->required()
                ->options( [
                    'NO' => 'NO',
                    'YES' => 'YES',
                ])
                ->default('NO'),
                Forms\Components\TextInput::make('barcode')
                ->label('Barcode')
                ->required()
                ->maxLength(20),
                Forms\Components\TextInput::make('dineinprice')
                ->label('Precio modulo 1')
                ->numeric()
                ->maxLength(8) // Restringe la longitud del texto
                ->prefix('$') // Agrega el símbolo de moneda
                ->extraInputAttributes([
                    'step' => '0.01', // Permite valores con dos decimales
                    'min' => '0', // Evita números negativos
                    'maxlength' => '8', // Asegura que el usuario no escriba más de 8 caracteres
                ])
                ->live(),
                Forms\Components\TextInput::make('takeoutprice')
                ->label('Precio modulo 2')
                ->numeric()
                ->maxLength(8) // Restringe la longitud del texto
                ->prefix('$') // Agrega el símbolo de moneda
                ->extraInputAttributes([
                    'step' => '0.01', // Permite valores con dos decimales
                    'min' => '0', // Evita números negativos
                    'maxlength' => '8', // Asegura que el usuario no escriba más de 8 caracteres
                ])
                ->live(),
                Forms\Components\TextInput::make('drivethruprice')
                ->label('Precio modulo 3')
                ->numeric()
                ->maxLength(8) // Restringe la longitud del texto
                ->prefix('$') // Agrega el símbolo de moneda
                ->extraInputAttributes([
                    'step' => '0.01', // Permite valores con dos decimales
                    'min' => '0', // Evita números negativos
                    'maxlength' => '8', // Asegura que el usuario no escriba más de 8 caracteres
                ])
                ->live(),
                Forms\Components\TextInput::make('DeliveryPrice')
                ->label('Precio modulo 4')
                ->numeric()
                ->maxLength(8) // Restringe la longitud del texto
                ->prefix('$') // Agrega el símbolo de moneda
                ->extraInputAttributes([
                    'step' => '0.01', // Permite valores con dos decimales
                    'min' => '0', // Evita números negativos
                    'maxlength' => '8', // Asegura que el usuario no escriba más de 8 caracteres
                ])
                ->live(),
                Forms\Components\Toggle::make('orderbyweight')
                ->label('Ordenar por Peso')
                ->required()
                ->inline(false),
                Forms\Components\Toggle::make('bar')
                ->label('Producto de Bar')
                ->required()
                ->inline(false),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('id'),
                Tables\Columns\TextColumn::make('menuitemtext')->label('Producto')
                ->searchable(),
                Tables\Columns\TextColumn::make('groups.menugrouptext')
                ->label('Grupo')
                ->sortable(),
                Tables\Columns\CheckboxColumn::make('menuiteminactive')->label('Inactivo')
                ->disabled(),
                Tables\Columns\TextColumn::make('menuitemtaxable')
                ->label(fn () => Taxes::getTaxName(1)) // Obtiene el nombre del impuesto 1
                ->formatStateUsing(fn ($state) => $state ? 'Sí' : 'No')
                ->disabled(),
                Tables\Columns\TextColumn::make('gstapplied')
                    ->label(fn () => Taxes::getTaxName(2)) // Obtiene el nombre del impuesto 2
                    ->formatStateUsing(fn ($state) => $state ? 'Sí' : 'No')
                    ->disabled(),
                Tables\Columns\TextColumn::make('liquortaxapplied')
                    ->label(fn () => Taxes::getTaxName(3)) // Obtiene el nombre del impuesto 3
                    ->formatStateUsing(fn ($state) => $state ? 'Sí' : 'No')
                    ->disabled(),
            ])
            ->filters([
                SelectFilter::make('Categoria')
                ->relationship('categories','menucategorytext')
                ->searchable()
                ->preload(),
                SelectFilter::make('Grupo')
                ->relationship('groups','menugrouptext')
                ->searchable()
                ->preload(),
                SelectFilter::make('tax_filter')
                ->label('Impuesto')
                ->options(self::getTaxOptions())
                ->default(null)
                ->query(function ($query, $state) {
                    if (empty($state)) return $query;
                    return $query->where(function ($q) use ($state) {
                        if (in_array(1, $state)) {
                            $q->orWhere('menuitemtaxable', 1);
                        }
                        if (in_array(2, $state)) {
                            $q->orWhere('gstapplied', 1);
                        }
                        if (in_array(3, $state)) {
                            $q->orWhere('liquortaxapplied', 1);
                        }
                    });
                }),
            ], layout: FiltersLayout::AboveContent)->filtersFormColumns(3)
            ->actions([
                Tables\Actions\EditAction::make(),
            ])
            ->bulkActions([
                // Tables\Actions\BulkActionGroup::make([
                //     Tables\Actions\DeleteBulkAction::make(),
                // ]),
            ]);
    }

    public static function getRelations(): array
    {
        return [
            //
        ];
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListProducts::route('/'),
            'create' => Pages\CreateProduct::route('/create'),
            'edit' => Pages\EditProduct::route('/{record}/edit'),
        ];
    }
    public static function getModelLabel(): string
    {
        return __(key: 'Producto');
    }
    public static function getPluralModelLabel(): string
    {
        return __(key: 'Productos');
    }
    public static function getTaxOptions(): array
    {
        return Taxes::pluck('taxname', 'id')->toArray();
    }
}
